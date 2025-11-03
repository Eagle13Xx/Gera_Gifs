from gif_creator.models import GeneratedGif
import os
import uuid
import base64
import requests
import time 
from io import BytesIO
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip
import google.generativeai as genai

RUNWAY_API_BASE_URL = "https://api.dev.runwayml.com/v1"
CLIPDROP_API_URL = "https://clipdrop-api.co/text-to-image/v1"


class AnimationService:

    def __init__(self, user, prompt, overlay_text=''):
        """
        Initializes the AnimationService.

        Args:
            user: The User object making the request.
            prompt (str): The initial text prompt provided by the user.
            overlay_text (str, optional): Text to overlay on the generated GIF. Defaults to ''.
        """
        self.user = user

        # --- API Configurations ---
        self.clipdrop_api_key = settings.CLIPDROP_API_KEY
        self.clipdrop_headers = {'x-api-key': self.clipdrop_api_key}
        self.runway_api_key = settings.RUNWAY_API_KEY
        self.runway_headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }

        # --- Prompt Enhancement with Gemini ---
        original_prompt = prompt
        print(f"--- Etapa 0: Aprimorando prompt com Gemini (Original: '{original_prompt}') ---")
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)

            model = genai.GenerativeModel('gemini-2.5-pro')  

            meta_prompt = (
                "Aprimore o seguinte prompt de usuário para gerar uma imagem mais detalhada, "
                "artística e de alta qualidade em uma API de IA (como Stable Diffusion/ClipDrop). "
                "Ex de melhoria "
                "Prompt Usuario: Uma manhã bonita em uma plantação de milho com o sol nascendo"
                "Prompt melhorado: (masterpiece, 8k, best quality:1.3), a beautiful morning in a corn field with the sun rising, vibrant golden hues reflecting off the corn leaves, (landscape:1.2), (atmospheric:1.1), (depth of field:1.1), (clear sky:1.2), (greenery details:1.3), (sunlight filtering through corn stalks:1.3), Negative prompt: (worst quality, low quality:1.4), blurry, ugly, text, watermark. Steps: 30, Sampler: DPM++ 2M Karras, CFG scale: 7."
                "e composição, mas mantenha a ideia central do usuário. "
                "Retorne APENAS o prompt aprimorado, sem nenhuma introdução ou texto extra.\n\n"
                f"Prompt do Usuário: \"{original_prompt}\""
            )

            response = model.generate_content(meta_prompt)
            if response.parts:
                enhanced_prompt_from_gemini = response.text.strip()
            else:
                print("!!! Resposta do Gemini vazia ou bloqueada. Usando prompt original. !!!")
                enhanced_prompt_from_gemini = original_prompt

            print(f"--- Prompt Aprimorado pelo Gemini: '{enhanced_prompt_from_gemini}' ---")

        except Exception as e:
            print(f"!!! Erro ao chamar a API do Gemini: {e}. Usando o prompt original. !!!")
            enhanced_prompt_from_gemini = original_prompt

        final_prompt_for_clipdrop =  enhanced_prompt_from_gemini

        self.prompt = final_prompt_for_clipdrop
        self.overlay_text = overlay_text.strip().strip('"\'')
        self.font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'fonte.ttf')
        self.output_filename = f"{uuid.uuid4()}.gif"
        self.output_path = os.path.join(settings.MEDIA_ROOT, 'ai_gifs', self.output_filename)

    def _generate_base_image_with_text(self):
        print("--- Etapa 1: Gerando imagem base com ClipDrop ---")
        print(f"--- Prompt Final Enviado para ClipDrop: {self.prompt} ---")
        files = {'prompt': (None, self.prompt, 'text/plain')}
        response = requests.post(CLIPDROP_API_URL, headers=self.clipdrop_headers, files=files)

        if response.ok:
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            print("--- Imagem gerada com sucesso pela ClipDrop ---")
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('error', response.text)
            except requests.exceptions.JSONDecodeError:
                error_message = response.text
            raise Exception(f"Erro na API ClipDrop ({response.status_code}): {error_message}")

        if self.overlay_text:
            if self.overlay_text:
                draw = ImageDraw.Draw(image)
                font_size = int(image.width / 12)
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                except IOError:
                    font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), self.overlay_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (image.width - text_width) / 2
            y = (image.height - text_height) * 0.85
            shadow_color = '#404040'
            draw.text((x - 2, y - 2), self.overlay_text, font=font, fill=shadow_color)
            draw.text((x + 2, y - 2), self.overlay_text, font=font, fill=shadow_color)
            draw.text((x - 2, y + 2), self.overlay_text, font=font, fill=shadow_color)
            draw.text((x + 2, y + 2), self.overlay_text, font=font, fill=shadow_color)
            draw.text((x, y), self.overlay_text, font=font, fill='white')

        return image

    def generate_animated_gif(self):
        """Orquestra todo o processo: imagem -> animação -> conversão para GIF."""
        # 1. Gera a imagem estática com o texto
        final_image_pil = self._generate_base_image_with_text()
        # Converte a imagem de RGBA para RGB antes de enviar.
        # Isso remove o canal de transparência que pode causar o erro no Runway.
        print("--- Convertendo imagem para RGB antes de enviar ---")
        final_image_rgb = final_image_pil.convert("RGB")

        buffered = BytesIO()
        # Salva a imagem RGB (pode usar JPEG que é mais leve, ou PNG)
        final_image_rgb.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        # Ajusta o data_uri para o formato correto
        data_uri = f"data:image/jpeg;base64,{base64_image}"

        # 2. Inicia a tarefa de animação no Runway
        print("--- Etapa 2: Enviando para animação no Runway... ---")
        start_payload = {
            "promptImage": data_uri,
            "model": "gen4_turbo",
            "duration": 3,
            "ratio": "960:960"
        }
        start_response = requests.post(f"{RUNWAY_API_BASE_URL}/image_to_video", headers=self.runway_headers,
                                       json=start_payload)

        if start_response.status_code != 200:
            raise Exception(f"Erro ao iniciar a tarefa no Runway: {start_response.text}")

        response_json = start_response.json()
        task_id = response_json['id']
        # --------------------------------

        print(f"--- Tarefa iniciada com ID: {task_id} ---")

        while True:
            print("--- Verificando status da tarefa... ---")
            status_response = requests.get(f"{RUNWAY_API_BASE_URL}/tasks/{task_id}", headers=self.runway_headers)
            status_data = status_response.json()

            if status_data['status'] == 'SUCCEEDED':
                # A resposta de sucesso pode ser uma lista, pegamos o primeiro item
                video_url = status_data['output'][0] if isinstance(status_data.get('output'),
                                                                   list) else status_data.get('output')
                print("--- Etapa 3: Vídeo gerado! URL:", video_url, "---")
                break
            elif status_data['status'] == 'FAILED':
                raise Exception(f"A tarefa no Runway falhou: {status_data}")

            time.sleep(5)

        print("--- Etapa 4: Baixando vídeo e preparando para conversão... ---")
        video_response = requests.get(video_url)

        temp_video_path = os.path.join(settings.MEDIA_ROOT, 'temp_videos', f'{uuid.uuid4()}.mp4')
        os.makedirs(os.path.dirname(temp_video_path), exist_ok=True)
        with open(temp_video_path, "wb") as f:
            f.write(video_response.content)

        clip = VideoFileClip(temp_video_path)

        print("--- Etapa 5: Aplicando compressão (redimensionamento e FPS)... ---")

        # 1. Redimensiona o vídeo para uma largura máxima de 480 pixels, mantendo a proporção.
        final_clip = clip.resized(width=480)

        target_fps = 12

        print("--- Etapa 6: Convertendo vídeo otimizado para GIF... ---")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # Usa o clipe redimensionado ('final_clip') e o novo FPS para criar o GIF.
        final_clip.write_gif(self.output_path, fps=target_fps)

        # Fecha os clipes para liberar memória
        final_clip.close()
        clip.close()

        os.remove(temp_video_path)

        gif_path = os.path.join(settings.MEDIA_URL, 'ai_gifs', self.output_filename)

        GeneratedGif.objects.create(
            user=self.user,
            prompt=self.prompt,
            overlay_text=self.overlay_text,
            gif_url=gif_path
        )
        return gif_path

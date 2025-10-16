# gif_creator/services.py
from gif_creator.models import GeneratedGif
import os
import uuid
import base64
import requests
import time  # <-- Importa a biblioteca 'time' para fazer pausas
from io import BytesIO
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip

# URL do modelo de GERAÇÃO DE IMAGEM (Hugging Face)
IMAGE_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# URLs da API do Runway (baseadas na nova documentação)
RUNWAY_API_BASE_URL = "https://api.dev.runwayml.com/v1"


class AnimationService:
    def __init__(self,user, prompt, overlay_text=''):
        # Configurações da API de Imagem (Hugging Face)
        self.user = user
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        self.hf_headers = {"Authorization": f"Bearer {self.hf_api_key}"}

        # Configurações da API de Animação (Runway) - agora direto com requests
        self.runway_api_key = settings.RUNWAY_API_KEY
        self.runway_headers = {
            "Authorization": f"Bearer {self.runway_api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"  # Header recomendado na documentação
        }

        self.prompt = f"{prompt}, beautiful, high quality, cinematic"
        self.overlay_text = overlay_text.strip().strip('"\'')

        self.font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'fonte.ttf')
        self.output_filename = f"{uuid.uuid4()}.gif"
        self.output_path = os.path.join(settings.MEDIA_ROOT, 'ai_gifs', self.output_filename)

    def _generate_base_image_with_text(self):
        # ... (este método para gerar a imagem com Pillow continua o mesmo de antes)
        print("--- Etapa 1: Gerando imagem base ---")
        payload = {"inputs": self.prompt}
        response = requests.post(IMAGE_MODEL_URL, headers=self.hf_headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Erro na API de Imagem: {response.text}")

        image = Image.open(BytesIO(response.content)).convert("RGBA")

        if self.overlay_text:
            draw = ImageDraw.Draw(image)
            font_size = int(image.width / 12)
            font = ImageFont.truetype(self.font_path, font_size)

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
        # --- CORREÇÃO APLICADA AQUI ---
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

        # 2. Define uma taxa de quadros (FPS) um pouco menor. 12 FPS é um bom equilíbrio
        #    entre fluidez e tamanho do arquivo para GIFs.
        target_fps = 12
        # --- FIM DAS ETAPAS DE COMPRESSÃO ---

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
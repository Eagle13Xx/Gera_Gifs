import traceback

from rest_framework import views, status, generics
from rest_framework.response import Response
from .permissions import IsSubscribedUser
from .serializers import GeneratedGifSerializer # Importe o novo serializer
from .models import GeneratedGif # Importe o modelo
from .services import AnimationService # Importe a nova classe
from subscriptions.models import Subscription

class GenerateImageView(views.APIView):
    permission_classes = [IsSubscribedUser]

    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            active_subscription = Subscription.objects.get(user=user, status='active')
            if active_subscription.gif_count >= active_subscription.plan.gif_limit:
                return Response(
                    {'error': 'Você atingiu o limite mensal de geração de GIFs para o seu plano.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Subscription.DoesNotExist:
            return Response({'error': 'Nenhuma assinatura ativa encontrada.'}, status=status.HTTP_403_FORBIDDEN)

        prompt = request.data.get('prompt')
        overlay_text = request.data.get('text')

        if not prompt:
            return Response({'error': 'A descrição da imagem é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = AnimationService(user=user, prompt=prompt, overlay_text=overlay_text)
            gif_url = service.generate_animated_gif()

            active_subscription.gif_count += 1
            active_subscription.save()

            full_gif_url = request.build_absolute_uri(gif_url)
            return Response({'gif_url': full_gif_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("\n" + "!" * 60)
            print("      OCORREU UMA EXCEÇÃO DURANTE A GERAÇÃO DO GIF")
            print("!" * 60)

            # Imprime o tipo do erro e a mensagem
            print(f"TIPO DE ERRO: {type(e).__name__}")
            print(f"MENSAGEM: {e}")

            # Imprime o traceback completo para sabermos a linha exata
            print("\n--- TRACEBACK COMPLETO ---")
            traceback.print_exc()

            print("!" * 60 + "\n")
            # FIM DO DIAGNÓSTICO

            # Retorna uma resposta 500 com a mensagem de erro para o frontend
            return Response({'error': f"Erro interno no servidor: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GifHistoryView(generics.ListAPIView):
    """
    Retorna a lista de GIFs gerados pelo usuário autenticado.
    """
    serializer_class = GeneratedGifSerializer

    def get_queryset(self):
        # Filtra os GIFs para retornar apenas os do usuário que fez a requisição
        return GeneratedGif.objects.filter(user=self.request.user)


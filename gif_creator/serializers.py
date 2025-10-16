from rest_framework import serializers
from .models import GeneratedGif


class GeneratedGifSerializer(serializers.ModelSerializer):
    gif_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedGif
        fields = ['id', 'prompt', 'overlay_text', 'gif_url', 'created_at']

    def get_gif_url(self, obj):
        """
        Este método é chamado automaticamente pelo SerializerMethodField.
        Ele constrói a URL absoluta para o arquivo do GIF.
        """
        # 'obj' é a instância do modelo GeneratedGif
        request = self.context.get('request')
        if request is None:
            return None

        # request.build_absolute_uri() pega o caminho relativo (obj.gif_url)
        # e o transforma em uma URL completa (ex: http://127.0.0.1:8000/media/...)
        return request.build_absolute_uri(obj.gif_url)
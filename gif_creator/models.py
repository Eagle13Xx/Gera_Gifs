from django.db import models
from django.conf import settings

class GeneratedGif(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gifs')
    prompt = models.TextField(verbose_name="Descrição (Prompt)")
    overlay_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Texto Sobreposto")
    gif_url = models.URLField(max_length=500, verbose_name="URL do GIF")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GIF de {self.user.username} - {self.created_at.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "GIF Gerado"
        verbose_name_plural = "GIFs Gerados"
        ordering = ['-created_at'] # Ordena do mais novo para o mais antigo
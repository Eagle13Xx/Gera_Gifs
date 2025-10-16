from django.urls import path
# gif_creator/urls.py
from .views import GenerateImageView, GifHistoryView # Importe a nova view

urlpatterns = [
    # ...
    path('generate-image/', GenerateImageView.as_view(), name='generate-image'),
    path('history/', GifHistoryView.as_view(), name='gif-history'), #
]
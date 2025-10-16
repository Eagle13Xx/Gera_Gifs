"""
Configuração do painel de administração do Django para o app 'subscriptions'.

Este arquivo define como os modelos Plan e Subscription são exibidos e
gerenciados no painel de administração do Django, facilitando a visualização
e a manutenção dos dados de planos e assinaturas de usuários.
"""

from django.contrib import admin
from .models import Plan, Subscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    Personaliza a exibição e o comportamento do modelo Plan no painel de administração.
    """
    # Define as colunas que serão exibidas na lista de planos.
    # Adicionamos 'gif_limit' para facilitar a visualização do limite de cada plano.
    list_display = ('name', 'price', 'cycle', 'gif_limit', 'is_active')

    # Adiciona filtros na barra lateral direita para facilitar a busca de planos.
    list_filter = ('is_active', 'cycle')

    # Adiciona uma barra de pesquisa que buscará pelo nome do plano.
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Personaliza a exibição e o comportamento do modelo Subscription no painel de admin.
    """
    # Define as colunas a serem exibidas na lista de assinaturas.
    # Adiciona 'gif_count' para uma visão rápida do uso atual do usuário.
    list_display = ('user', 'plan', 'status', 'gif_count', 'cancellation_requested', 'end_date')

    # Adiciona filtros na barra lateral para encontrar assinaturas por status, plano ou
    # se o cancelamento foi solicitado.
    list_filter = ('status', 'plan', 'cancellation_requested')

    # Habilita uma barra de busca que pesquisa nos campos especificados.
    # O uso de '__' permite pesquisar em campos de modelos relacionados (ex: user__username).
    search_fields = ('user__username', 'plan__name', 'asaas_subscription_id')


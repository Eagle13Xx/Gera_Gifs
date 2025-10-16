# subscriptions/urls.py

from django.urls import path


from .views import PlanListView, CreateSubscriptionView, AsaasWebhookView, UserSubscriptionDetailView, \
    CancelSubscriptionView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('create-subscription/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('webhook/', AsaasWebhookView.as_view(), name='asaas-webhook'), # 2. Adicione a nova URL
    path('my-subscription/', UserSubscriptionDetailView.as_view(), name='my-subscription-detail'),
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel-subscription'),

]
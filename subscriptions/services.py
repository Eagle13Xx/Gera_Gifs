# subscriptions/services.py
import time
import requests
from django.conf import settings
from .models import Subscription
from datetime import date

# URLs da API do Hugginface
IMAGE_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# URLs da API do Runway
RUNWAY_API_BASE_URL = "https://api.dev.runwayml.com/v1"

class AsaasService:
    def __init__(self):
        self.api_key = settings.ASAAS_API_KEY
        self.api_url = settings.ASAAS_API_URL.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': self.api_key
        }

    def create_customer(self, user):
        search_url = f"{self.api_url}/customers?cpfCnpj={user.taxId}"
        response = requests.get(search_url, headers=self.headers)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('data'):
            return response_data['data'][0]['id']
        url = f"{self.api_url}/customers"
        payload = {"name": user.get_full_name(), "email": user.email, "mobilePhone": user.cellphone,
                   "cpfCnpj": user.taxId}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()['id']

    def create_subscription(self, customer_id, plan):
        url = f"{self.api_url}/subscriptions"
        clean_plan_name = plan.name.encode('ascii', 'ignore').decode('utf-8')
        success_redirect_url = f"{settings.FRONTEND_URL}/payment/status"

        payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": float(plan.price) / 100,
            "nextDueDate": date.today().isoformat(),
            "cycle": plan.cycle,
            "description": f"Assinatura do plano {clean_plan_name.strip()}",
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_first_payment_url_for_subscription(self, subscription_id):
        """Busca as cobranças de uma assinatura e retorna a URL da primeira."""
        # A API pode levar um instante para gerar a cobrança, então esperamos um pouco
        time.sleep(2)

        url = f"{self.api_url}/payments?subscription={subscription_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        payments_data = response.json()

        if payments_data.get('data'):
            # Pega a primeira cobrança da lista
            first_payment = payments_data['data'][0]
            return first_payment.get('invoiceUrl')

        # Fallback caso algo dê errado
        return None

    def create_subscription_and_get_url(self, user, plan):
        """Orquestra a criação do cliente, da assinatura, a busca pela URL e salva no banco."""
        # ETAPA 1: Criar a assinatura
        customer_id = self.create_customer(user)
        subscription_data = self.create_subscription(customer_id, plan)
        subscription_id = subscription_data['id']

        # Salva a assinatura no banco de dados
        Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'asaas_subscription_id': subscription_id,
                'status': 'pending',
            }
        )

        # ETAPA 2: Usar o ID da assinatura para buscar a URL de pagamento
        payment_url = self.get_first_payment_url_for_subscription(subscription_id)

        return payment_url

    def cancel_subscription(self, asaas_subscription_id):
        url = f"{self.api_url}/subscriptions/{asaas_subscription_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
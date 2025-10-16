from django.http import Http404
from rest_framework.permissions import AllowAny
import json
from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
import datetime
from .services import AsaasService
from django.conf import settings
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer

# A PlanListView não muda, continua igual.
class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

# Esta é a view principal que vamos alterar.
class CreateSubscriptionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        user = request.user

        # Lógica para impedir assinatura duplicada
        if hasattr(user, 'subscription') and user.subscription.status == 'active':
            return Response(
                {'error': 'Você já possui uma assinatura ativa.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
            asaas_service = AsaasService()
            payment_url = asaas_service.create_subscription_and_get_url(user, plan)

            return Response({'payment_url': payment_url})

        except Plan.DoesNotExist:
            return Response({'error': 'Plano não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AsaasWebhookView(views.APIView):
    """
    Recebe e processa webhooks do Asaas para atualizar o status e as datas das assinaturas.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        asaas_token = request.headers.get('Asaas-Access-Token')
        if not asaas_token or asaas_token != settings.ASAAS_WEBHOOK_SECRET:
            return Response({'status': 'error', 'message': 'Token inválido.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = json.loads(request.body)
            event_type = payload.get('event')

            if event_type in ['PAYMENT_RECEIVED', 'PAYMENT_CONFIRMED']:
                payment_data = payload.get('payment', {})
                asaas_subscription_id = payment_data.get('subscription')

                if asaas_subscription_id:
                    subscription = Subscription.objects.get(asaas_subscription_id=asaas_subscription_id)

                    # --- LÓGICA DE ATUALIZAÇÃO DE STATUS E DATAS ---
                    subscription.status = 'active'
                    subscription.gif_count = 0

                    # Calcula a data de expiração baseada no ciclo do plano
                    now = timezone.now()
                    if subscription.plan.cycle == 'MONTHLY':
                        # Adiciona aproximadamente 31 dias para garantir a cobertura do mês
                        end_date = now + datetime.timedelta(days=31)
                    elif subscription.plan.cycle == 'YEARLY':
                        end_date = now + datetime.timedelta(days=366)
                    else:
                        end_date = now + datetime.timedelta(days=31)  # Fallback padrão

                    subscription.end_date = end_date
                    subscription.next_billing_date = end_date  # A próxima cobrança coincide com o fim do período

                    subscription.save()

                    # Atualiza o status do usuário
                    user = subscription.user
                    user.has_active_subscription = True
                    user.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Subscription.DoesNotExist:
            return Response({'status': 'success', 'message': 'Assinatura não encontrada'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Erro inesperado no webhook: {e}")
            return Response({'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Obter Detalhes da Assinatura do Usuário ---
class UserSubscriptionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_object(self):
        try:
            return Subscription.objects.get(user=self.request.user, status='active')
        except Subscription.DoesNotExist:
            raise Http404


# --- Cancelar Assinatura ---
class CancelSubscriptionView(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            # 1. Tenta encontrar uma assinatura que possa ser cancelada
            # ativa e que ainda não teve o cancelamento solicitado).
            subscription = Subscription.objects.get(
                user=request.user,
                status='active',
                cancellation_requested=False
            )

            # Se encontrar, cancela normalmente...
            asaas_service = AsaasService()
            asaas_service.cancel_subscription(subscription.asaas_subscription_id)

            subscription.cancellation_requested = True
            subscription.save()

            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Subscription.DoesNotExist:
            # 2. Se a primeira busca falhou, vamos descobrir o porquê.
            try:
                # Tentamos encontrar uma assinatura que está ativa, mas JÁ FOI CANCELADA.
                already_canceled_sub = Subscription.objects.get(
                    user=request.user,
                    status='active',
                    cancellation_requested=True
                )

                # 3. Se encontrar, montamos a mensagem de erro personalizada.
                end_date_formatted = "data indefinida"
                if already_canceled_sub.end_date:
                    end_date_formatted = already_canceled_sub.end_date.strftime('%d/%m/%Y')

                message = f"Sua assinatura já foi cancelada e expira em {end_date_formatted}."

                # Retorna um erro 400 (Bad Request), que indica que a requisição é inválida
                # porque a ação não pode ser executada novamente.
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

            except Subscription.DoesNotExist:
                # 4. Se mesmo assim não encontrar nada, então o usuário realmente não tem
                #    nenhuma assinatura ativa para cancelar.
                return Response(
                    {'error': 'Nenhuma assinatura ativa encontrada para cancelar.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

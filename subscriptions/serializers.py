from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'price', 'cycle']

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer que retorna os dados da assinatura de forma "plana" (flat),
    incluindo todos os campos necessários para o frontend.
    """
    # Define os campos do plano que queremos "puxar" para o nível principal
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.IntegerField(source='plan.price', read_only=True)
    plan_cycle = serializers.CharField(source='plan.cycle', read_only=True)
    plan_gif_limit = serializers.IntegerField(source='plan.gif_limit', read_only=True)

    class Meta:
        model = Subscription
        # Esta é a lista final e correta de campos que a API deve retornar
        fields = [
            'id',
            'plan_name',
            'plan_price',
            'plan_cycle',
            'plan_gif_limit',
            'status',
            'gif_count',
            'cancellation_requested',
            'end_date',
            'next_billing_date',
            'created_at',
        ]
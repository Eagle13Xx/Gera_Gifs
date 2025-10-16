from django.db import models
from django.conf import settings


class Plan(models.Model):
    # Crie uma lista de choices para o ciclo
    CYCLE_CHOICES = [
        ('MONTHLY', 'Mensal'),
        ('YEARLY', 'Anual'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(help_text="Preço em centavos")
    cycle = models.CharField(
        max_length=20,
        choices=CYCLE_CHOICES,
        default='MONTHLY'
    )
    gif_limit = models.IntegerField(
        default=30,
        help_text="Número de GIFs que o usuário pode gerar por mês neste plano."
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('canceled', 'Cancelada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    asaas_subscription_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    gif_count = models.IntegerField(
        default=0,
        help_text="Número de GIFs gerados no ciclo de faturamento atual."
    )
    cancellation_requested = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    cellphone = models.CharField(max_length=20, blank=False, null=False, verbose_name="Telefone Celular")
    taxId = models.CharField(max_length=14, blank=False, null=False, verbose_name="CPF",unique=True)
    gateway_customer_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    has_active_subscription = models.BooleanField(default=False, verbose_name="Possui Assinatura Ativa?")

    @property
    def get_active_subscription(self):
        try:
            return self.subscriptions.get(status='active', end_date__gte=timezone.now())
        except self.subscriptions.model.DoesNotExist:
            return None
        except self.subscriptions.model.MultipleObjectsReturned:
            return self.subscriptions.filter(status='active', end_date__gte=timezone.now()).first()
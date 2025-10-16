from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User

class UserSerializer(serializers.ModelSerializer):
    # Campo extra para informar se o usuário tem assinatura ativa
    subscription_active = serializers.BooleanField(source='has_active_subscription', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'cellphone', 'taxId', 'subscription_active']


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Adiciona uma validação explícita para o email, garantindo que seja único.
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Já existe um usuário com este e-mail.")]
    )

    # Tornamos a senha write_only para que ela não seja retornada em nenhuma requisição GET.
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        # Lista de campos que o frontend enviará para o registro.
        fields = ('username', 'password', 'email', 'first_name', 'taxId', 'cellphone')

    def create(self, validated_data):
        """
        Este método é chamado quando a validação passa.
        Ele cria o usuário e garante que a senha seja criptografada (hashed).
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            password=validated_data['password'],
            taxId=validated_data['taxId'],
            cellphone=validated_data['cellphone']
        )
        return user
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Validador que exige o cumprimento de regras de complexidade para a senha.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula (A-Z)."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra minúscula (a-z)."),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("A senha deve conter pelo menos um número (0-9)."),
                code='password_no_number',
            )
        if not re.search(r'[\W_]', password):  # \W corresponde a caracteres não alfanuméricos
            raise ValidationError(
                _("A senha deve conter pelo menos um caractere especial (ex: !@#$%)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Sua senha deve conter pelo menos uma letra maiúscula, uma minúscula, um número e um caractere especial."
        )
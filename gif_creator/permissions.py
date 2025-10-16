from rest_framework.permissions import BasePermission

class IsSubscribedUser(BasePermission):
    message = "Apenas usuários com assinatura ativa podem gerar GIFs."

    def has_permission(self, request, view):
        # A propriedade `has_active_subscription` que criamos no modelo User
        return request.user and request.user.is_authenticated and request.user.has_active_subscription
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей"""

    class Meta:
        model = User
        fields = "__all__"


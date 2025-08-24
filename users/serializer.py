from rest_framework import serializers

from .models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей"""

    class Meta:
        model = User
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели платежей"""

    class Meta:
        model = Payment
        fields = "__all__"

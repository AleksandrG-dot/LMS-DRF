from rest_framework import serializers

from .models import Payment, PaymentCourseStripe, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "groups",
            "user_permissions",
            "password",  # без этого поля не передается пароль в UsersCreateAPIView
        )


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели платежей"""

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentCourseStripeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели платежей за курс через Stripe - PaymentCourseStripe"""

    class Meta:
        model = PaymentCourseStripe
        fields = "__all__"

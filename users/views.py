from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny

from users.models import Payment, User
from users.serializer import PaymentSerializer, UserSerializer


class UsersCreateAPIView(generics.CreateAPIView):
    """Дженерик для создания пользователя"""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(serializer.validated_data['password'])  # было user.set_password(user.password)
        user.save()


class UsersListApiView(generics.ListAPIView):
    """Дженерик для получения списка пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsersRetrieveApiView(generics.RetrieveAPIView):
    """Дженерик для получения пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsersUpdateApiView(generics.UpdateAPIView):
    """Дженерик для обновления данных пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsersDestroyApiView(generics.DestroyAPIView):
    """Дженерик для удаления пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели платежей"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("course", "lesson", "payment_method")
    ordering_fields = ("date",)

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import Payment, Subscription, User
from users.serializer import PaymentSerializer, UserSerializer


class UsersCreateAPIView(generics.CreateAPIView):
    """Дженерик для создания пользователя"""

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(
            serializer.validated_data["password"]
        )  # было user.set_password(user.password)
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


class SubscriptionAPIView(APIView):
    """Представление на установку или удаление подписки пользователя на курс."""

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course"],
            properties={
                "course": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID курса для подписки/отписки",
                )
            },
        ),
        responses={
            201: openapi.Response(
                description="Успешная операция подписки/отписки",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение о результате операции",
                        ),
                        "status": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="Статус подписки (True - подписан, False - отписан)",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "course": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Сообщение о ошибке"
                        )
                    },
                ),
            ),
            404: "Курс не найден",
        },
    )
    def post(self, *args, **kwargs):
        # получаем объект пользователя
        user = self.request.user

        # Получаем id курса из self.reqests.data
        course_id = self.request.data.get("course")
        if not course_id:
            return Response({"course": ["This field is required."]}, status=400)

        # Получаем объект курса из базы
        course_item = generics.get_object_or_404(Course, id=course_id)

        # Получаем объекты подписок по текущему пользователю и курсу
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = f"Подписка удалена на курс '{course_item.title}'"
            status = False
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = f"Подписка добавлена на курс '{course_item.title}'"
            status = True

        return Response({"message": message, "status": status}, status=201)

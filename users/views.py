from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, serializers, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import Payment, PaymentCourseStripe, Subscription, User
from users.serializer import (PaymentCourseStripeSerializer, PaymentSerializer,
                              UserSerializer)
from users.services import (check_stripe_payment, create_stripe_price,
                            create_stripe_product, create_stripe_session)


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

        return Response({"message": message, "status": status})


class PaymentsCourseStripeCreateAPIView(generics.CreateAPIView):
    """Дженерик для модели платежа за курс через экваиринг stripe.com - PaymentCourseStripe"""

    serializer_class = PaymentCourseStripeSerializer
    queryset = PaymentCourseStripe.objects.all()

    def perform_create(self, serializer):

        # Получаем курс из валидированных данных (сразу курс, а не его id)
        course = serializer.validated_data["course"]

        # Проверка, не нулевая ли цена у курса
        if not course.price or course.price <= 0:
            raise serializers.ValidationError(
                f"Курс не для продажи. Цена: {course.price}"
            )

        # Создание продукта, цены и сессии в Stripe.com
        try:
            product = create_stripe_product(course.title)
            price = create_stripe_price(product, course.price)
            session_id, payment_link = create_stripe_session(price)
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка Stripe: {str(e)}")

        # Пометка об этом ужасе. Пол дня бился, со всеми вариантами сериализатора. Оказалось makemigrations не
        # создавала в миграциях поле session_id и не было понятно почему. И, соответственно, его не было в БД.
        # Оказалось что в модели в конце session_if = model.CharField(...), стояла запятая, на которую никто
        # ни как не ругался, но она как-то мешала создавать миграции.
        # Так же сериализатор не давал нормально отработать, так как если в нём указать только поле course, то эта ...
        # не даёт сохранить другие поля при serializer.save(), а если разрешить все поля "__all__", то в постамане
        # со всех требует ввести user и amount. Что является бредом, разрешающим указать другого пользователя и цену.
        # Хотя потом это все равно все перетрется внутри этого метода. Как вариант рассматривал использование
        # PaymentCourseStrip.objects.create(). Но это некрасиво: вылазить из рамок метода и работать с моделью
        # напрямую. В итоге проблему решил расстановкой полей null и blank в модели у полей, где оставил blank=False
        # только у поля Course.

        # Ниже использовал текст для попыток сохранить и что бы каждый раз не мучить stripe.com
        # session_id="cs_test_a191x7KVqTozxJRD2EwQxUck65WHWqxFGnOdY05cF5CKULJIVtXoz0EuXa"
        # payment_link="dostal.tvar.ru/davai_rabotai?filter=serializator_tvar&prishlos_peredelatdel_model_null_blank "

        # Сохранение платежа
        serializer.save(
            user=self.request.user,
            course=course,
            amount=course.price,
            session_id=session_id,
            link=payment_link,
            is_paid=False,  # Статус - не оплачен (он же по умолчанию)
        )


class CheckStripePaymentStatusAPIView(generics.CreateAPIView):
    """
    Представление для проверки статуса оплаты через Stripe
    """

    # Создаст запись в модели Payment при успешной оплате

    def create(self, request, *args, **kwargs):

        results = check_stripe_payment()
        if results["errors"]:
            return Response(
                {
                    "message": f"Проверено {results['checked']} платежей. Успешно оплачено: {results['paid']}",
                    "errors": results["errors"],
                    "status": "with_error",
                },
                status=status.HTTP_207_MULTI_STATUS,
            )
        else:
            return Response(
                {
                    "message": f"Проверено {results['checked']} платежей. Успешно оплачено: {results['paid']}",
                    "status": "without_error",
                },
                status=status.HTTP_200_OK,
            )

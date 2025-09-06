from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import (PaymentViewSet, UsersCreateAPIView,
                         UsersDestroyApiView, UsersListApiView,
                         UsersRetrieveApiView, UsersUpdateApiView,
                         SubscriptionAPIView)

app_name = UsersConfig.name


router_payment = SimpleRouter()  # Роутер для представления платежей
router_payment.register(r"payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("register/", UsersCreateAPIView.as_view(), name="register"),
    #  В текущей реализации DRF и библиотеки JWT-аутентификации класс TokenObtainPairView уже
    #  имеет встроенные права AllowAny (писать .as_view(permission_classes = (AllowAny,)) не надо)
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("list/", UsersListApiView.as_view(), name="users_list"),
    path("<int:pk>/", UsersRetrieveApiView.as_view(), name="user"),
    path("<int:pk>/update/", UsersUpdateApiView.as_view(), name="users_update"),
    path("<int:pk>/delete/", UsersDestroyApiView.as_view(), name="users_delete"),
    path("subs/", SubscriptionAPIView.as_view(), name="subscription"),
]

# urlpatterns += router_user.urls
urlpatterns += router_payment.urls

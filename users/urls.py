from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import PaymentViewSet, UserViewSet

app_name = UsersConfig.name

router_user = SimpleRouter()  # Роутер для представления пользователей
router_user.register(r"user", UserViewSet, basename="user")

router_payment = SimpleRouter()  # Роутер для представления платежей
router_payment.register(r"payment", PaymentViewSet, basename="payment")

urlpatterns = []

urlpatterns += router_user.urls
urlpatterns += router_payment.urls

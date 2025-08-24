from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import UserViewSet

app_name = UsersConfig.name

router_user = SimpleRouter() # Роутер для представления пользователей
router_user.register(r"user", UserViewSet, basename="user")

urlpatterns = []

urlpatterns += router_user.urls

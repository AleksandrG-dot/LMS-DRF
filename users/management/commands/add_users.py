from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Загрузка данных о пользователях из фикстур."

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        User.objects.all().delete()

        # Загружаем данные из фикстуры users_fixture.json
        call_command("loaddata", "users_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded users from fixture"))

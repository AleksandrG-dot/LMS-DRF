from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import Payment


class Command(BaseCommand):
    help = "Загрузка данных о платежах из фикстур."

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Payment.objects.all().delete()

        # Загружаем данные из фикстуры payments_fixture.json
        call_command("loaddata", "payments_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded payments from fixture"))

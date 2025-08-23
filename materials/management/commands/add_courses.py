from django.core.management import call_command
from django.core.management.base import BaseCommand

from materials.models import Course


class Command(BaseCommand):
    help = "Загрузка данных о курсах из фикстур."

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Course.objects.all().delete()

        # Загружаем данные из фикстуры courses_fixture.json
        call_command("loaddata", "courses_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))

from django.core.management import call_command
from django.core.management.base import BaseCommand

from materials.models import Lesson


class Command(BaseCommand):
    help = "Загрузка данных о уроках из фикстур."

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Lesson.objects.all().delete()

        # Загружаем данные из фикстуры lessons_fixture.json
        call_command("loaddata", "lessons_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))

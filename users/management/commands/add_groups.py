from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загрузка данных о группах из фикстур."

    def handle(self, *args, **kwargs):

        # Загружаем данные из фикстуры groups_fixture.json
        call_command("loaddata", "groups_fixture.json")
        self.stdout.write(
            self.style.SUCCESS("Successfully loaded groups from fixture")
        )

from django.core.management import BaseCommand, call_command
from polling.models import Poll


class Command(BaseCommand):
    help = "Добавление тестовых данных с фикстуры"

    def handle(self, *args, **kwargs):
        Poll.objects.all().delete()
        call_command("loaddata", "fixture_poll.json")
        self.stdout.write(self.style.SUCCESS("Выполнено успешно"))

import json

from django.core.management import BaseCommand, call_command

from config.settings import BASE_DIR
from polling.models import Poll, Level


class Command(BaseCommand):
    help = "Добавление с очищением, новых викторин"

    def handle(self, *args, **kwargs):
        Poll.objects.all().delete()
        # call_command("loaddata", "fixture_poll.json")
        path = BASE_DIR / "poll.json"
        with open(path, encoding="utf-8") as f:
            read_data = json.load(f)

        for poll_data in read_data:
            id_level = Level.objects.get(id=poll_data["level"])
            Poll.objects.create(
                id_poll=poll_data["id"],
                quest=poll_data["question_text"],
                code=poll_data["code"],
                answers=poll_data["options"],
                current_answer=poll_data["correct_answer"],
                hint=poll_data["explanation"],
                level=id_level,
            )

            self.stdout.write(self.style.SUCCESS(f"{poll_data["id"]} - Выполнено успешно"))

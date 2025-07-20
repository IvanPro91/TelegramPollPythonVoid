import random

from asgiref.sync import sync_to_async
from django.contrib.postgres.fields import ArrayField
from django.db import models

from bot.models import TelegramUser


class Level(models.Model):
    """Уровень сложности"""

    LVL_LESSONS = (
        ("EASY", "Легкий"),
        ("MEDIUM", "Средний"),
        ("HARD", "Сложный"),
    )
    name_level = models.CharField(max_length=150, choices=LVL_LESSONS)

    def __str__(self):
        return self.name_level

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"


class Poll(models.Model):
    """Для викторин"""

    id_poll = models.CharField(max_length=200, verbose_name="Номер созданной викторины", null=True)
    quest = models.CharField(max_length=200, verbose_name="Вопрос")
    answers = ArrayField(models.CharField(max_length=200), blank=True, default=list, verbose_name="Список ответов")
    current_answer = models.PositiveIntegerField(verbose_name="Номер правильного ответа")
    hint = models.CharField(max_length=250, verbose_name="Объяснение")
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.quest

    @sync_to_async
    def do_poll(self, poll_id):
        """anonymous - если приватный, то накапливаем баллы"""
        if poll_id:
            random_poll = Poll.objects.get(id_poll=poll_id)
        else:
            poll = Poll.objects.all()
            random_poll = poll[random.randint(0, len(poll) - 1)]
        data = {
            "pk": random_poll.pk,
            "poll": random_poll,
            "id_poll": random_poll.id_poll,
            "question": random_poll.quest,
            "options": [answer for answer in random_poll.answers],
            "explanation": random_poll.hint,
            "correct_option_id": random_poll.current_answer,
        }
        return data

    @sync_to_async
    def to_dict(self):
        """anonymous - если приватный, то накапливаем баллы"""
        poll = Poll.objects.all()
        random_poll = poll[random.randint(0, len(poll) - 1)]
        data = {
            "pk": random_poll.pk,
            "poll": random_poll,
            "id_poll": random_poll.id_poll,
            "question": random_poll.quest,
            "options": [answer for answer in random_poll.answers],
            "explanation": random_poll.hint,
            "correct_option_id": random_poll.current_answer,
        }
        return data

    @classmethod
    @sync_to_async
    def get_all_poll(cls):
        all_poll = list(cls.objects.all())
        return [poll.to_dict() for poll in all_poll]

    class Meta:
        verbose_name = "Викторина"
        verbose_name_plural = "Викторины"


class PrivatePoll(models.Model):
    id_poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="private")
    id_created_poll = models.TextField(null=False, blank=False, verbose_name="Номер викторины после создания")
    id_telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="private")
    create_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    user_answer = models.BooleanField(default=False)
    ball = models.PositiveIntegerField(default=1)
    correct_option_id = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id_created_poll} {self.user_answer}"

    @classmethod
    @sync_to_async
    def add_private_poll(cls, pk, id_created_poll, id_telegram_user, correct_option_id, ball):
        cls.objects.create(
            id_poll=pk,
            id_created_poll=id_created_poll,
            id_telegram_user=id_telegram_user,
            status=False,
            user_answer=False,
            ball=ball,
            correct_option_id=correct_option_id,
        )

    @classmethod
    @sync_to_async
    def get_user_private_poll(cls, user, id_created_poll):
        get_poll = cls.objects.get(id_created_poll=id_created_poll, id_telegram_user=user)
        username = get_poll.id_telegram_user.username or "None"
        return {"id_poll": get_poll.id_poll.id_poll, "user": username}

    @classmethod
    @sync_to_async
    def get_private_poll(cls, qst_id):
        get_poll = cls.objects.get(id_created_poll=qst_id)
        username = get_poll.id_telegram_user.username or ""
        first_name = get_poll.id_telegram_user.first_name or ""
        last_name = get_poll.id_telegram_user.last_name or ""

        return {"id_poll": get_poll.id_poll.id_poll, "user": f"{username} {first_name} {last_name}"}

    @classmethod
    @sync_to_async
    def set_answer_poll(cls, answer_ids, user: "TelegramUser", id_created_poll):
        get_poll = cls.objects.filter(id_created_poll=id_created_poll).first()
        if get_poll:
            if int(get_poll.correct_option_id) == int(answer_ids[0]):
                get_poll.user_answer = True
                get_poll.status = True
                user.count_winner += get_poll.ball
                user.save()
                get_poll.save()
                position = user.get_user_positions()
                print("Правильный ответ!", user, user.count_winner)
                return position, user.count_winner
            else:
                if user.count_winner > get_poll.ball:
                    user.count_winner -= get_poll.ball
                    user.save()
                get_poll.user_answer = True
                get_poll.status = False
                get_poll.save()

                position = user.get_user_positions()
                print(position)
                print("Ответ не правильный!")
                return position, user.count_winner
        return None, None

    class Meta:
        verbose_name = "Приватная викторина"
        verbose_name_plural = "Приватные викторины"

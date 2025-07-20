import datetime

from asgiref.sync import sync_to_async
from django.db import models


class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True, verbose_name="Номер пользователя")
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name="Имя пользователя")
    first_name = models.CharField(max_length=100, verbose_name="Имя", null=True)
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Фамилия")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Последняя активность")
    chat_id = models.TextField(verbose_name="Номер чата", default="")
    message_thread_id = models.IntegerField(default=0, verbose_name="Номер чата", null=True)
    count_winner = models.PositiveIntegerField(default=0, verbose_name="Количество побед")
    position_user = models.PositiveIntegerField(default=0, verbose_name="Позиция пользователя в рейтинге")

    def __str__(self):
        return f"{self.username or self.first_name}"

    @classmethod
    @sync_to_async
    def get_user_from_chat_id(cls, message_chat_id):
        return cls.objects.filter(user_id=message_chat_id).first()

    @sync_to_async
    def set_count_winner(self, count):
        self.count_winner -= count
        self.save()
        return True

    @sync_to_async
    def set_position_winner(self, position):
        if self.position_user < position:
            self.position_user = position
            self.save()
            return False, "Вы опустились"
        elif self.position_user > position:
            self.position_user = position
            self.save()
            return True, "Вы поднялись"
        return False, "Без изменений"

    def get_user_positions(self):
        higher_count = TelegramUser.objects.filter(count_winner__gt=self.count_winner).count()
        return higher_count + 1

    @classmethod
    @sync_to_async
    def get_or_create_user(
        cls,
        message_thread_id: int,
        chat_id: int,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
    ):
        get_user = cls.objects.filter(user_id=user_id).first()
        if not get_user:
            get_user = cls.objects.create(
                message_thread_id=message_thread_id,
                chat_id=chat_id,
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
        else:
            get_user.last_activity = datetime.datetime.now()
            get_user.message_thread_id = message_thread_id
            get_user.username = username
            get_user.first_name = first_name
            get_user.last_name = last_name
            get_user.save()
        return get_user

    class Meta:
        verbose_name = "Телеграм пользователя"
        verbose_name_plural = "Телеграм пользователи"


class TelegramMsg(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    msg = models.TextField(verbose_name="Сообщение пользователя")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение от пользователя"
        verbose_name_plural = "Сообщения от пользователя"

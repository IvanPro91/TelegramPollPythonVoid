from django.contrib import admin

from bot.models import TelegramMsg, TelegramUser


@admin.register(TelegramUser)
class TelegramUserModel(admin.ModelAdmin):
    list_display = [field.name for field in TelegramUser._meta.fields]
    list_filter = ("count_winner",)


@admin.register(TelegramMsg)
class TelegramMsgModel(admin.ModelAdmin):
    list_display = [field.name for field in TelegramMsg._meta.fields]

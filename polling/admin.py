from django.contrib import admin

from polling.models import Poll, Level, PrivatePoll


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Poll._meta.fields]
    search_fields = ("id_poll", "quest")


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Level._meta.fields]


@admin.register(PrivatePoll)
class PrivatePollAdmin(admin.ModelAdmin):
    list_display = [
        "id_poll",
        "id_created_poll",
        "id_telegram_user",
        "create_at",
        "status",
        "user_answer",
        "ball",
        "correct_option_id",
    ]
    search_fields = ("id_created_poll",)

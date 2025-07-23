from django.shortcuts import render

from bot.models import TelegramUser


# Create your views here.
def get_profile(request, user_id):
    user = TelegramUser.objects.get(user_id=user_id)
    context = {"user": user}
    return render(request, template_name="profile.html", context=context)

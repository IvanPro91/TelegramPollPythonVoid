import random

from django.shortcuts import render

from config.settings import TEXT_COINS_CARD
from polling.models import Poll


def get_polling(request):
    poll = Poll.objects.all()
    random_poll = poll[random.randint(0, len(poll) - 1)]
    context = {"poll": random_poll, "TEXT_COINS_CARD": TEXT_COINS_CARD}
    return render(request, "index.html", context=context)

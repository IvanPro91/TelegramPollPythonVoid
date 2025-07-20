import random

from django.shortcuts import render

from polling.models import Poll


def get_polling(request):
    poll = Poll.objects.all()
    random_poll = poll[random.randint(0, len(poll) - 1)]
    context = {"poll": random_poll}
    return render(request, "index.html", context=context)

from django.urls import path

from home.apps import HomeConfig
from home.views import get_polling

app_name = HomeConfig.name

urlpatterns = [
    path("", get_polling, name="home"),
]

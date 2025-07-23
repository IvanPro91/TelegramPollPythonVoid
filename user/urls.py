from django.urls import path

from user.apps import UserConfig
from user.views import get_profile

app_name = UserConfig.name

urlpatterns = [
    path("<str:user_id>", get_profile, name="profile"),
]

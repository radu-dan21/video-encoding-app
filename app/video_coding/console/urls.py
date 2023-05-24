from django.urls import path
from django.views.generic import RedirectView

from video_coding.console.views import OriginalVideoFileListView


app_name = "console"
urlpatterns = [
    path("", RedirectView.as_view(url="home")),
    path("home", OriginalVideoFileListView.as_view(), name="home"),
]

from django.urls import path
from django.views.generic import RedirectView

from video_coding.console.views import (
    OriginalVideoFileCreateView,
    OriginalVideoFileDeleteView,
    OriginalVideoFileDetailsView,
    OriginalVideoFileListView,
)


app_name = "console"
urlpatterns = [
    path("", RedirectView.as_view(url="home")),
    path("home", OriginalVideoFileListView.as_view(), name="home"),
    path(
        "ovf/<int:ovf_id>", OriginalVideoFileDetailsView.as_view(), name="ovf_details"
    ),
    path("create", OriginalVideoFileCreateView.as_view(), name="ovf_create"),
    path(
        "ovf/<int:pk>/delete",
        OriginalVideoFileDeleteView.as_view(),
        name="ovf_delete",
    ),
]

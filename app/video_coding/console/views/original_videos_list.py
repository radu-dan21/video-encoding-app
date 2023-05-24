from django.views.generic import ListView

from video_coding.entities.models import OriginalVideoFile


class OriginalVideoFileListView(ListView):
    model = OriginalVideoFile
    paginate_by = 10
    template_name = "console/ovf_list.html"

    def get_queryset(self):
        return OriginalVideoFile.objects.all().order_by("-id")

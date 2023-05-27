from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView

from video_coding.console.forms import OriginalVideoFileForm
from video_coding.entities.models import OriginalVideoFile


class OriginalVideoFileView(View):
    template_name = "console/ovf_details.html"

    @staticmethod
    def _get_or_404(ovf_id: int) -> OriginalVideoFile:
        try:
            return OriginalVideoFile.objects.get(id=ovf_id)
        except OriginalVideoFile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        ovf: OriginalVideoFile = self._get_or_404(ovf_id=kwargs.get("ovf_id"))
        form = OriginalVideoFileForm(instance=ovf)
        return render(request, self.template_name, {"form": form})


class OriginalVideoFileDeleteView(SuccessMessageMixin, DeleteView):
    model = OriginalVideoFile
    success_url = reverse_lazy("console:home")
    template_name = "console/ovf_delete.html"
    success_message = "Original video file <%(name)s> deleted successfully!"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            **{attr: getattr(self.object, attr) for attr in ("name",)},
        )

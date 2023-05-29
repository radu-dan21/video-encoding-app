from itertools import chain

from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, FormView, ListView

from video_coding.console.forms import (
    EncodedVideoFileFormset,
    EncodedVideoFileFormsetHelper,
    InformationFilterResultFormset,
    InformationFilterResultFormsetHelper,
    OriginalVideoFileCreateForm,
    OriginalVideoFileDetailsReadonlyForm,
)
from video_coding.entities.models import (
    EncodedVideoFile,
    InformationFilterResult,
    OriginalVideoFile,
)


class OriginalVideoFileListView(ListView):
    model = OriginalVideoFile
    paginate_by = 10
    template_name = "console/ovf_list.html"

    def get_queryset(self):
        return OriginalVideoFile.objects.all().order_by("-id")


class OriginalVideoFileCreateView(SuccessMessageMixin, FormView):
    template_name = "console/ovf_create.html"
    form_class = OriginalVideoFileCreateForm
    success_url = reverse_lazy("console:home")
    success_message = "Original video file created successfully!"


class OriginalVideoFileDetailsView(View):
    template_name = "console/ovf_details.html"

    @staticmethod
    def _get_or_404(ovf_id: int) -> OriginalVideoFile:
        try:
            return OriginalVideoFile.objects.get(id=ovf_id)
        except OriginalVideoFile.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        ovf: OriginalVideoFile = self._get_or_404(ovf_id=kwargs.get("ovf_id"))
        form = OriginalVideoFileDetailsReadonlyForm(instance=ovf)
        ifr_formset = InformationFilterResultFormset(
            queryset=InformationFilterResult.objects.filter(video=ovf),
        )

        evfs = EncodedVideoFile.objects.filter(original_video_file=ovf)
        evf_formset = EncodedVideoFileFormset(queryset=evfs)

        cfrs = list(chain.from_iterable([e.comparison_filters for e in evfs]))
        comparison_filters: list[str] = list({cfr.video_filter.name for cfr in cfrs})

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "ifr_formset": ifr_formset,
                "ifr_helper": InformationFilterResultFormsetHelper(),
                "evf_formset": evf_formset,
                "evf_helper": EncodedVideoFileFormsetHelper(
                    extra_fields=comparison_filters,
                ),
            },
        )


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

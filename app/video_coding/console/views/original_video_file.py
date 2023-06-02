from itertools import chain

from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.uploadedfile import UploadedFile
from django.http import Http404
from django.http.response import HttpResponse
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
    ComparisonFilter,
    EncodedVideoFile,
    InformationFilterResult,
    OriginalVideoFile,
)
from video_coding.tasks import run_ovf_workflow


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

    def form_valid(self, form: OriginalVideoFileCreateForm) -> HttpResponse:
        ovf, file_path = form.save()
        if not file_path:
            self.handle_uploaded_file(self.request.FILES["file"], ovf.file_path)
        run_ovf_workflow.delay(ovf_id=ovf.id, file_path=file_path)
        return super().form_valid(form)

    @staticmethod
    def handle_uploaded_file(file: UploadedFile, destination: str) -> None:
        with open(destination, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)


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

        comparison_filters_names: list[str] = self._get_comparison_filters_names(evfs)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "ifr_formset": ifr_formset,
                "ifr_helper": InformationFilterResultFormsetHelper(),
                "evf_formset": evf_formset,
                "evf_helper": EncodedVideoFileFormsetHelper(
                    extra_fields=comparison_filters_names,
                ),
            },
        )

    @staticmethod
    def _get_comparison_filters_names(evfs: list[EncodedVideoFile]) -> list[str]:
        cfrs: list[ComparisonFilter] = list(
            chain.from_iterable([e.comparison_filters for e in evfs])
        )
        return list(
            ComparisonFilter.objects.filter(
                id__in={cfr.video_filter.id for cfr in cfrs}
            ).values_list(
                "name", flat=True
            )  # used in order to preserve db ordering
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

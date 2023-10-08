import math

from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Prefetch
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, FormView, ListView

from video_coding.console.forms import (
    BDMetricFormset,
    BDMetricFormsetHelper,
    EncodedVideoFileFormset,
    EncodedVideoFileFormsetHelper,
    InformationFilterResultFormset,
    InformationFilterResultFormsetHelper,
    OriginalVideoFileCreateForm,
    OriginalVideoFileDetailsReadonlyForm,
)
from video_coding.entities.models import (
    ComparisonFilter,
    ComparisonFilterResult,
    EncodedVideoFile,
    OriginalVideoFile,
)
from video_coding.entities.models.graph import EncodingTimeGraph, MetricGraph
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
        ovf = (
            OriginalVideoFile.objects.filter(id=ovf_id)
            .prefetch_related(
                Prefetch(
                    "comparison_filter_results",
                    to_attr="cfrs",
                    queryset=(
                        ComparisonFilterResult.objects.select_related(
                            "comparison_filter"
                        )
                    ),
                ),
            )
            .first()
        )
        if not ovf:
            raise Http404
        return ovf

    def get(self, request, *args, **kwargs):
        ovf_id: int = kwargs.get("ovf_id")
        ovf: OriginalVideoFile = self._get_or_404(ovf_id=ovf_id)
        form = OriginalVideoFileDetailsReadonlyForm(instance=ovf)
        ifr_formset = InformationFilterResultFormset(
            queryset=ovf.info_filter_results.all(),
        )
        evfs = (
            EncodedVideoFile.objects.filter(original_video_file_id=ovf_id)
            .select_related("decoded_video_file")
            .prefetch_related(
                Prefetch(
                    "decoded_video_file__filter_results",
                    to_attr="cfrs",
                    queryset=(
                        ComparisonFilterResult.objects.select_related(
                            "comparison_filter"
                        ).only("value", "comparison_filter__name")
                    ),
                ),
            )
        )
        evf_formset = EncodedVideoFileFormset(queryset=evfs)
        comparison_filters = self._get_comparison_filters(evfs)
        graphs = []
        if not ovf.is_in_progress:
            graphs = self._get_graphs(ovf_id)
        bd_metrics_formset = BDMetricFormset(
            queryset=ovf.bd_metrics.exclude(bd_rate=math.nan),
        )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "ifr_formset": ifr_formset,
                "ifr_helper": InformationFilterResultFormsetHelper(
                    extra_fields=["description"],
                ),
                "evf_formset": evf_formset,
                "evf_helper": EncodedVideoFileFormsetHelper(
                    extra_fields=[cf.name for cf in comparison_filters],
                ),
                "graphs": graphs,
                "bd_metrics_formset": bd_metrics_formset,
                "bd_metrics_helper": BDMetricFormsetHelper(),
            },
        )

    @staticmethod
    def _get_comparison_filters(
        evfs: list[EncodedVideoFile],
    ) -> list[ComparisonFilter]:
        cfs = {cfr.comparison_filter for cfr in evfs[0].decoded_video_file.cfrs}
        return list(sorted(cfs, key=lambda cf: cf.id))

    @staticmethod
    def _get_graphs(ovf_id: int) -> list[str]:
        return [
            *EncodingTimeGraph.objects.filter(original_video_file_id=ovf_id),
            *MetricGraph.objects.filter(original_video_file_id=ovf_id),
        ]


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

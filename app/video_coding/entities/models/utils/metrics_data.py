import math

from pandas import DataFrame


class MetricsData:
    """
    Used for extracting data from an experiment, for the purpose of
    computing BDMetric, EncodingTimeGraph and MetricGraph instances
    """

    # columns that do not depend on associated ComparisonFilter instances
    COMMON_COLUMNS: list[str] = [
        "encoder",
        "encoder setting",
        "bitrate (kbps)",
        "log10 bitrate (kbps)",
        "encoding time (seconds)",
    ]

    def __init__(self, ovf_id: int):
        self.ovf_id = ovf_id
        self.data_frame = self._compute()

    def _compute(self) -> DataFrame:
        from video_coding.entities.models.filter import ComparisonFilterResult
        from video_coding.entities.models.video_file import EncodedVideoFile

        evfs = (
            EncodedVideoFile.objects.select_related(
                "encoder_setting__encoder", "decoded_video_file"
            )
            .only(
                "encoding_time",
                "ffprobe_info",
                "decoded_video_file__id",
                "encoder_setting__name",
                "encoder_setting__encoder__name",
            )
            .filter(original_video_file_id=self.ovf_id)
        )
        cfrs = (
            ComparisonFilterResult.objects.select_related("comparison_filter")
            .only(
                "value",
                "video_to_compare_id",
                "comparison_filter__id",
                "comparison_filter__name",
            )
            .filter(reference_video_id=self.ovf_id)
            .order_by("comparison_filter__id")
        )

        comparison_filters = list({cfr.comparison_filter for cfr in cfrs})
        comparison_filters.sort(key=lambda vf: vf.id)

        column_names = self.COMMON_COLUMNS + [vf.name for vf in comparison_filters]

        dvf_data_mapping: dict[int, list] = {
            e.decoded_video_file.id: [
                e.encoder_setting.encoder.name,
                e.encoder_setting.name,
                e.bitrate,
                math.log(e.bitrate),
                e.encoding_time,
            ]
            for e in evfs
        }

        for cfr in cfrs:
            dvf_data_mapping[cfr.video_to_compare_id].append(cfr.value)

        return DataFrame(
            data=sorted(dvf_data_mapping.values(), key=lambda d: d[2]),
            columns=column_names,
        )

    def get_metric_column_names(self) -> list[str]:
        return list(
            reversed(
                [
                    c
                    for c in self.data_frame.columns
                    if c not in MetricsData.COMMON_COLUMNS
                ]
            )
        )

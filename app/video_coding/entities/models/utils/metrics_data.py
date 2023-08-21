import math

from pandas import DataFrame


class MetricsData:
    COMMON_COLUMNS: list[str] = [
        "codec",
        "codec setting",
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
                "video_encoding__codec", "decoded_video_file"
            )
            .only(
                "encoding_time",
                "ffprobe_info",
                "decoded_video_file__id",
                "video_encoding__name",
                "video_encoding__codec__name",
            )
            .filter(original_video_file_id=self.ovf_id)
        )
        cfrs = (
            ComparisonFilterResult.objects.select_related("video_filter")
            .only(
                "value",
                "video_to_compare_id",
                "video_filter__id",
                "video_filter__name",
            )
            .filter(reference_video_id=self.ovf_id)
            .order_by("video_filter__id")
        )

        video_filters = list({cfr.video_filter for cfr in cfrs})
        video_filters.sort(key=lambda vf: vf.id)

        column_names = self.COMMON_COLUMNS + [vf.name for vf in video_filters]

        dvf_data_mapping: dict[int, list] = {
            e.decoded_video_file.id: [
                e.video_encoding.codec.name,
                e.video_encoding.name,
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

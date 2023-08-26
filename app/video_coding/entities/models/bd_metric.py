import itertools

import pandas

from bjontegaard import bd_psnr, bd_rate
from django.db import models

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.video_encoding import Codec


class BDMetric(BaseModel):
    original_video_file = models.ForeignKey(
        "OriginalVideoFile",
        on_delete=models.CASCADE,
        related_name="bd_metrics",
    )
    video_filter = models.ForeignKey(
        "ComparisonFilter",
        on_delete=models.CASCADE,
    )
    reference_codec = models.ForeignKey(
        "Codec",
        on_delete=models.CASCADE,
        related_name="reference_metrics",
    )
    test_codec = models.ForeignKey(
        "Codec",
        on_delete=models.CASCADE,
        related_name="test_metrics",
    )
    bd_rate = models.FloatField()
    bd_metric = models.FloatField()

    @classmethod
    def compute(cls, ovf, metrics_data):
        from video_coding.entities.models.filter import ComparisonFilter

        def prepare_values(v1_, v2_, metric_name_):
            res = []
            for v in (v1_, v2_):
                done = False
                while not done:
                    done = True
                    for i in range(1, len(v.index)):
                        idx = v.index[i]
                        prev_idx = v.index[i - 1]
                        if v[metric_name_][idx] < v[metric_name_][prev_idx]:
                            v = v.drop([idx])
                            done = False
                            break
                res.append(v)
            return res

        df: pandas.DataFrame = metrics_data.data_frame

        # preserve db ordering
        codecs = list(Codec.objects.filter(name__in=set(df.codec)))
        codec_data = {c: df[df.codec == c.name] for c in codecs}

        metrics_column_names = metrics_data.get_metric_column_names()
        metric_dict = ComparisonFilter.objects.in_bulk(
            metrics_column_names,
            field_name="name",
        )

        for c1, c2 in itertools.combinations(codec_data.keys(), r=2):
            v1, v2 = (codec_data[c] for c in (c1, c2))
            for metric_name in metrics_data.get_metric_column_names():
                v1p, v2p = prepare_values(v1, v2, metric_name)
                bd_metric_args = [
                    getattr(v1p, "bitrate (kbps)"),
                    getattr(v1p, metric_name),
                    getattr(v2p, "bitrate (kbps)"),
                    getattr(v2p, metric_name),
                    "akima",
                    False,
                ]
                bd_rate_ = bd_rate(*bd_metric_args)
                bd_metric = bd_psnr(*bd_metric_args)
                cls.objects.create(
                    name=f"OVF {ovf.id} - {c1.name} vs {c2.name} - {metric_name}",
                    original_video_file=ovf,
                    video_filter=metric_dict[metric_name],
                    reference_codec=c1,
                    test_codec=c2,
                    bd_rate=bd_rate_,
                    bd_metric=bd_metric,
                )

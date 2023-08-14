import plotly.graph_objects as go

from plotly.subplots import make_subplots

from video_coding.entities.models import ComparisonFilter, EncodedVideoFile


class VideoGraph:
    COLORS = ["red", "blue", "yellow", "green", "orange"]

    def __init__(self, comparison_filter_name: str, evfs: list[EncodedVideoFile]):
        self._cf = ComparisonFilter.objects.get(name=comparison_filter_name)
        self._evfs = evfs

    def to_html(self) -> str:
        figure = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("BD-Rate", "Bitrate/Encoding time"),
        )
        evfs = self._evfs
        encodings = [evf.video_encoding for evf in evfs if evf.encoding_time]
        codecs = {enc.codec for enc in encodings}

        for idx, codec in enumerate(codecs):
            codec_evfs = list(
                filter(
                    lambda evf: evf.video_encoding.codec == codec,
                    evfs,
                )
            )
            data = [
                (
                    evf,
                    (dvf := evf.decoded_video_file),
                    dvf.filter_results.get(video_filter=self._cf),
                )
                for evf in codec_evfs
            ]
            data.sort(key=lambda tpl: tpl[0].bitrate)
            xy = [(tpl[0].bitrate, tpl[2].value) for tpl in data]
            x, y = list(zip(*xy))
            color = self.COLORS[idx % len(self.COLORS)]
            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    line={"color": color},
                    marker={"symbol": 104, "size": 10},
                    mode="lines+markers+text",
                    name=codec.name,
                ),
                row=1,
                col=1,
            )
            x1y1 = [(tpl[0].bitrate, tpl[0].encoding_time) for tpl in data]
            x1, y1 = list(zip(*x1y1))
            figure.add_trace(
                go.Scatter(
                    x=x1,
                    y=y1,
                    line={"color": color},
                    marker={"symbol": 104, "size": 10},
                    mode="lines+markers+text",
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

        figure.update_layout(height=600, width=1180)

        return figure.to_html()

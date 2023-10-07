import plotly.express as px

from django.core.validators import RegexValidator
from django.db import models

from video_coding.entities.models.base import BaseModel
from video_coding.entities.models.utils import MetricsData


class BaseGraph(BaseModel):
    """
    Base class that defines the common behavior of
    all types of graphs used throughout the project
    """

    REL_PATH_TO_OVF: str = "graphs/"

    original_video_file = models.ForeignKey(
        "OriginalVideoFile",
        on_delete=models.CASCADE,
    )

    file_path = models.CharField(
        blank=True,
        default="",
        validators=[RegexValidator(regex=r"^(.+)\.html")],
    )

    def create_graph_file(self, metrics_data: MetricsData) -> None:
        graph_html: str = self.generate(metrics_data)
        with open(self.file_path, "w") as f:
            f.write(graph_html)

    def generate(self, metrics_data) -> str:
        raise NotImplementedError

    def to_html(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class EncodingTimeGraph(BaseGraph):
    """
    Represents the graph that illustrates the relationship between the
    encoding time and bitrates of encoded videos, associated with an OriginalVideoFile
    """

    def generate(self, metrics_data: MetricsData) -> str:
        figure = px.scatter(
            metrics_data.data_frame,
            x="log10 bitrate (kbps)",
            y="encoding time (seconds)",
            hover_data=["bitrate (kbps)", "codec setting"],
            color="codec",
            symbol="codec",
            trendline="ols",
        )
        figure.update_layout(
            height=500,
            width=1000,
            title=dict(
                text="Encoding time graph",
                font=dict(size=32),
                automargin=True,
                yref="paper",
            ),
            font=dict(size=16),
        )
        return figure.to_html()


class MetricGraph(BaseGraph):
    """
    Represents the graph that illustrates the relationship between the
    bitrates and ComparisonFilterResults of encoded videos,
    associated with an OriginalVideoFile
    (1 MetricGraph for each ComparisonFilter selected for an OriginalVideoFile)
    """

    video_filter = models.ForeignKey(
        "ComparisonFilter",
        on_delete=models.CASCADE,
    )

    def generate(self, metrics_data: MetricsData) -> list[str]:
        vf_name: str = self.video_filter.name
        figure = px.line(
            metrics_data.data_frame,
            x="log10 bitrate (kbps)",
            y=self.video_filter.name,
            hover_data=["bitrate (kbps)", "codec setting"],
            color="codec",
            symbol="codec",
        )
        figure.update_layout(
            height=500,
            width=1000,
            title=dict(
                text=f"{vf_name} graph",
                font=dict(size=32),
                automargin=True,
                yref="paper",
            ),
            font=dict(size=16),
        )
        return figure.to_html()

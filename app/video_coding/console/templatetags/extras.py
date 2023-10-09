from django import template
from django.utils.safestring import mark_safe

from video_coding.entities.models import BaseGraph, OriginalVideoFile


register = template.Library()


@register.filter(needs_autoescape=True)
def ovf_status_html(ovf: OriginalVideoFile, autoescape=True):
    Status = OriginalVideoFile.Status
    # status: (alert_class, message)
    ovf_status_html_mapping: dict[Status, tuple[str, str]] = {
        Status.DONE: ("alert alert-success", "Workflow completed successfully!"),
        Status.COPYING: ("alert-warning", "Copying original video!"),
        Status.READY: ("alert-warning", "Video processing did not start yet!"),
        Status.INFO_METRICS: (
            "alert-warning",
            "Original video metrics are being computed!",
        ),
        Status.ENCODING: ("alert-warning", "Child video files are being encoded!"),
        Status.COMPARISON_METRICS: (
            "alert-warning",
            "Child video(s) metrics are being computed!",
        ),
        Status.FAILED: (
            "alert-danger",
            f"Workflow failed with error: {ovf.error_message}",
        ),
    }
    html_to_render: str = ""
    alert_message_tuple: tuple[str, str] | None = ovf_status_html_mapping[ovf.status]
    if alert_message_tuple:
        alert_class, message = alert_message_tuple
        html_to_render = f"""
            <div class="alert alert-fixed {alert_class}" role="alert">
                {message} {ovf_status_icon(ovf)}
            </div>
        """
    return mark_safe(html_to_render)


@register.filter(needs_autoescape=True)
def ovf_status_icon(ovf: OriginalVideoFile, autoescape=True):
    Status = OriginalVideoFile.Status
    ovf_status_icon_class_mapping: dict[Status, str] = {
        Status.DONE: "bi bi-check",
        Status.FAILED: "bi bi-x",
    }
    default_class: str = "spinner-border spinner-border-sm"
    css_class: str = ovf_status_icon_class_mapping.get(ovf.status, default_class)
    return mark_safe(f"""<span class="{css_class}"></span>""")


@register.filter(needs_autoescape=True)
def ovf_status_color(ovf: OriginalVideoFile, autoescape=True):
    Status = OriginalVideoFile.Status
    ovf_status_color_mapping: dict[Status, str] = {
        Status.DONE: "#155724",
        Status.FAILED: "#721c24",
    }
    default_color: str = "#856404"
    return mark_safe(ovf_status_color_mapping.get(ovf.status, default_color))


@register.filter(needs_autoescape=True)
def load_graph(graph: BaseGraph, autoescape=True):
    return graph.to_html()

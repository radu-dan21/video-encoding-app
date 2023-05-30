from django import template
from django.utils.safestring import mark_safe

from video_coding.entities.models import OriginalVideoFile


register = template.Library()


@register.filter(needs_autoescape=True)
def ovf_status_html(ovf: OriginalVideoFile, autoescape=True):
    Status = OriginalVideoFile.Status
    # status: (alert_class, message) | None
    ovf_status_html_mapping: dict[Status, tuple[str, str] | None] = {
        Status.DONE: None,
        Status.READY: ("alert-warning", "Video processing did not start yet!"),
        Status.ENCODING: ("alert-warning", "Child video files are being encoded!"),
        Status.METRICS: ("alert-warning", "Metrics are being computed!"),
        Status.FAILED: (
            "alert-danger",
            f"Workflow failed with error: <{ovf.error_message}>!",
        ),
    }
    html_to_render: str = ""
    alert_message_tuple: tuple[str, str] | None = ovf_status_html_mapping[ovf.status]
    if alert_message_tuple:
        alert_class, message = alert_message_tuple
        html_to_render = f"""
            <hr>
                <div class="alert {alert_class}" role="alert">
                    {message}
                </div>
            <hr>
        """
    return mark_safe(html_to_render)

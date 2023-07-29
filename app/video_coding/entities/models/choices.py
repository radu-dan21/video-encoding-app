from django.utils.translation import gettext_lazy as _


VALID_VIDEO_FILE_EXTENSION_LIST: list[str] = [
    "webm",
    "mkv",
    "flv",
    "vob",
    "ogv",
    "ogg",
    "rrc",
    "gifv",
    "mng",
    "mov",
    "avi",
    "qt",
    "wmv",
    "yuv",
    "y4m",
    "rm",
    "asf",
    "amv",
    "mp4",
    "m4p",
    "m4v",
    "mpg",
    "mp2",
    "mpeg",
    "mpe",
    "mpv",
    "m4v",
    "svi",
    "3gp",
    "3g2",
    "mxf",
    "roq",
    "nsv",
    "flv",
    "f4v",
    "f4p",
    "f4a",
    "f4b",
    "mod",
]

DEFAULT_VIDEO_EXT_CHOICE: tuple = ("", _("---"))
VALID_VIDEO_FILE_CHOICES_LIST: list[tuple[str, str]] = [DEFAULT_VIDEO_EXT_CHOICE] + [
    (ext, _(ext)) for ext in VALID_VIDEO_FILE_EXTENSION_LIST
]

VIDEO_FILE_NAME_REGEX: str = r"({})".format(
    "|".join(
        [f"({ext})" for ext in VALID_VIDEO_FILE_EXTENSION_LIST],
    ),
)

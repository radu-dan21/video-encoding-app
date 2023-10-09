import json

from typing import Any

from video_coding.utils.shell_utils import ShellOperations


class FFPROBE:
    CMD: str = (
        "ffprobe -loglevel warning -print_format json "
        "-show_format -show_streams {input}"
    )

    @classmethod
    def call(cls, input_file_path: str) -> dict:
        """
        FFPROBE command wrapper
        :param input_file_path: Path to the input video to be analyzed with ffprobe
        :return: ffprobe response, partially truncated to match
        """
        out = ShellOperations.call_bash_cmd(cls.CMD.format(input=input_file_path))
        return cls._modify_ffprobe_info_to_match_schema(json.loads(out))

    @classmethod
    def _modify_ffprobe_info_to_match_schema(cls, ffprobe_info: dict) -> dict:
        expected_stream_keys: list[str] = list(
            cls.SCHEMA["properties"]["streams"]["items"]["properties"].keys()
        )
        expected_format_keys: list[str] = list(
            cls.SCHEMA["properties"]["format"]["properties"].keys()
        )

        modified_streams_data: list[dict] = [
            {k: v for k, v in stream.items() if k in expected_stream_keys}
            for stream in ffprobe_info["streams"]
        ]
        modified_format_data: dict = {
            k: v for k, v in ffprobe_info["format"].items() if k in expected_format_keys
        }

        return {
            "streams": modified_streams_data,
            "format": modified_format_data,
        }

    SCHEMA: dict[str, Any] = {
        "type": "object",
        "properties": {
            "streams": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "codec_name": {"type": "string"},
                        "codec_long_name": {"type": "string"},
                        "profile": {"type": "string"},
                        "width": {"type": "integer"},
                        "height": {"type": "integer"},
                        "coded_width": {"type": "integer"},
                        "coded_height": {"type": "integer"},
                        "pix_fmt": {"type": "string"},
                        "color_range": {"type": "string"},
                        "field_order": {"type": "string"},
                        "r_frame_rate": {"type": "string"},
                        "avg_frame_rate": {"type": "string"},
                        "time_base": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
            },
            "format": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "nb_streams": {"type": "integer"},
                    "format_name": {"type": "string"},
                    "format_long_name": {"type": "string"},
                    "duration": {"type": "string"},
                    "size": {"type": "string"},
                    "bit_rate": {"type": "string"},
                    "probe_score": {"type": "integer"},
                },
                "additionalProperties": True,
            },
        },
        "required": ["streams", "format"],
    }

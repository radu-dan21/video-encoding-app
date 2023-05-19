import subprocess

from time import perf_counter


class FFMPEG:
    @classmethod
    def call(cls, args: list[str]) -> float:
        start_time: float = perf_counter()
        subprocess.run(
            ["ffmpeg"] + args + ["-y", "-loglevel", "error"], capture_output=True,
        )
        return perf_counter() - start_time


class Decode:
    @classmethod
    def call(cls, input_file_path: str, output_file_path: str) -> float:
        return FFMPEG.call(
            args=[
                "-i",
                input_file_path,
                "c:v",
                "rawvideo",
                "pix-fmt",
                "yuvv442",
                output_file_path,
            ],
        )

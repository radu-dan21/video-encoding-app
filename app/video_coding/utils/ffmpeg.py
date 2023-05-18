import subprocess

from time import perf_counter


class FFMPEG:
    @classmethod
    def call(
        cls, input_file_path: str, args: list[str], output_file_path: str
    ) -> float:
        start_time: float = perf_counter()
        subprocess.run(
            ["ffmpeg", "-i", f"{input_file_path}", "-y", "-loglevel", "error"]
            + args
            + [f"{output_file_path}"],
            capture_output=True,
        )
        return perf_counter() - start_time


class Decode:
    @classmethod
    def call(cls, input_file_path: str, output_file_path: str) -> float:
        return FFMPEG.call(
            input_file_path=input_file_path,
            output_file_path=output_file_path,
            args=[
                "c:v",
                "rawvideo",
                "pix-fmt",
                "yuvv442",
            ],
        )

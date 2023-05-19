import subprocess

from time import perf_counter


class FFMPEG:
    @classmethod
    def call(
        cls, args: list[str], capture_output: bool = False
    ) -> tuple[float, bytes | None]:
        start_time: float = perf_counter()
        completed_process: subprocess.CompletedProcess = subprocess.run(
            ["ffmpeg"]
            + args
            + ["-y", "-loglevel", "error"]
            + ["|&", "grep", "Parsed_", "2>&1", "tee"]
            if capture_output
            else [],
            capture_output=capture_output,
        )
        end_time: float = perf_counter()
        return end_time - start_time, completed_process.stdout


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
        )[0]
import subprocess

from time import perf_counter


class FFMPEG:
    @staticmethod
    def __call_bash_cmd(cmd: str) -> str:
        popen = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out, _err = popen.communicate(cmd.encode())
        popen.wait()
        return out.decode("utf-8")

    @classmethod
    def call(cls, args: list[str]) -> tuple[float, str]:
        start_time: float = perf_counter()
        output: str = cls.__call_bash_cmd(" ".join(["ffmpeg"] + args))
        end_time: float = perf_counter()
        return end_time - start_time, output


class Decode:
    @classmethod
    def call(cls, input_file_path: str, output_file_path: str) -> float:
        return FFMPEG.call(
            args=[
                "-y",
                "-i",
                input_file_path,
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                "yuyv422",
                output_file_path,
            ],
        )[0]

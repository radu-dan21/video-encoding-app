import subprocess

from time import perf_counter


class FFMPEG:
    @classmethod
    def call(cls, args: list[str]) -> tuple[float, str]:
        """
        FFMPEG command wrapper
        :param args: list of arguments for the ffmpeg command
        :return: execution time for the ffmpeg command and its output
        """
        start_time: float = perf_counter()
        output: str = cls.__call_bash_cmd(" ".join(["ffmpeg"] + args))
        end_time: float = perf_counter()
        return end_time - start_time, output

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


class Decode:
    @classmethod
    def call(cls, input_file_path: str, output_file_path: str) -> float:
        """
        Decodes a previously encoded video file
        :param input_file_path: Encoded video file path
        :param output_file_path: Path of the decoded video file
        :return: execution time of the decoding process
        """
        return FFMPEG.call(
            args=[
                "-y",
                "-i",
                f'"{input_file_path}"',
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                "yuyv422",
                output_file_path,
            ],
        )[0]

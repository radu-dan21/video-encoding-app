from time import perf_counter

from video_coding.utils.shell_utils import ShellOperations


class FFMPEG:
    @classmethod
    def call(cls, args: list[str]) -> tuple[float, str]:
        """
        FFMPEG command wrapper
        :param args: list of arguments for the ffmpeg command
        :return: execution time for the ffmpeg command and its output
        """
        start_time: float = perf_counter()
        output: str = ShellOperations.call_bash_cmd(" ".join(["ffmpeg"] + args))
        end_time: float = perf_counter()
        return end_time - start_time, output


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
                "-loglevel",
                "warning",
                "-i",
                f'"{input_file_path}"',
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                "yuyv422",
                output_file_path,
            ],
        )[0]

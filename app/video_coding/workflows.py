from video_coding.entities.models import (
    ComparisonFilter,
    ComparisonFilterResult,
    DecodedVideoFile,
    EncodedVideoFile,
    InformationFilter,
    InformationFilterResult,
    OriginalVideoFile,
    VideoEncoding,
)


class PrepareMainWorkflow:
    """
    Used for creating child video files and filter results for an OriginalVideoFile
    """

    def __init__(
        self,
        ovf_id: int,
        encoding_ids: list[int],
        info_filter_ids: list[int],
        comparison_filter_ids: list[int],
    ):
        self.ovf = OriginalVideoFile.objects.get(id=ovf_id)
        self.encodings = VideoEncoding.objects.filter(id__in=encoding_ids)
        self.info_filters = InformationFilter.objects.filter(id__in=info_filter_ids)
        self.comparison_filters = ComparisonFilter.objects.filter(
            id__in=comparison_filter_ids,
        )

    def run(self) -> None:
        encoded_video_files: list[EncodedVideoFile] = self.create_encoded_video_files()
        decoded_video_files: list[DecodedVideoFile] = self.create_decoded_video_files(
            encoded_video_files,
        )
        self.create_info_filter_results()
        self.create_comparison_filter_results(decoded_video_files)

    def create_encoded_video_files(self) -> list[EncodedVideoFile]:
        def _get_evf_extension(enc_: VideoEncoding) -> str:
            enc_ext: str = enc_.video_extension
            return (
                enc_ext
                if enc._meta.get_field("video_extension").get_default() != enc_ext
                else self.ovf.extension
            ).strip(" .")

        encoded_video_files: list[EncodedVideoFile] = []
        for enc in self.encodings:
            evf_extension: str = _get_evf_extension(enc)
            name: str = f"evf_{enc.name}_ovf_{self.ovf.id}"
            encoded_video_files.append(
                EncodedVideoFile.objects.create(
                    name=name,
                    file_name=f"{name}.{evf_extension}".replace(" ", ""),
                    original_video_file=self.ovf,
                    video_encoding=enc,
                ),
            )
        return encoded_video_files

    def create_decoded_video_files(
        self, encoded_video_files: list[EncodedVideoFile]
    ) -> list[DecodedVideoFile]:
        extension: str = "mkv"
        decoded_video_files: list[EncodedVideoFile] = []
        for evf in encoded_video_files:
            name: str = f"dvf_{evf.video_encoding.name}_evf_{evf.id}_ovf_{self.ovf.id}"
            decoded_video_files.append(
                DecodedVideoFile.objects.create(
                    name=name,
                    file_name=f"{name}.{extension}".replace(" ", ""),
                    encoded_video_file=evf,
                )
            )
        return decoded_video_files

    def create_info_filter_results(self) -> None:
        for if_ in self.info_filters:
            InformationFilterResult.objects.create(
                name=f"{if_.name}_ovf_{self.ovf.id}",
                video_filter=if_,
                video=self.ovf,
            )

    def create_comparison_filter_results(
        self,
        decoded_video_files: list[DecodedVideoFile],
    ) -> None:
        for cf in self.comparison_filters:
            for dvf in decoded_video_files:
                ComparisonFilterResult.objects.create(
                    name=f"{cf.name}_ovf_{self.ovf.id}_dvf_{dvf.id}",
                    video_filter=cf,
                    video_to_compare=dvf,
                    reference_video=self.ovf,
                )


def revert_back(ovf_id: int) -> None:
    """
    Deletes all child video files and filter results for an OriginalVideoFile
    Only used for testing and debugging purposes
    :param ovf_id: id of the OriginalVideoFile
    """
    ovf = OriginalVideoFile.objects.get(id=ovf_id)
    ovf.status = OriginalVideoFile.Status.READY
    ovf.error_message = ""
    ovf.ffprobe_info = {}

    ovf.save()

    ovf.encoded_video_files.all().delete()
    ovf.info_filter_results.all().delete()
    ovf.comparison_filter_results.all().delete()

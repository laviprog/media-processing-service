import subprocess

from src import log
from src.embedding_subtitles.enums import AppearanceType
from src.embedding_subtitles.exceptions import EmbeddingSubtitlesException


class EmbeddingSubtitlesService:
    """
    Service for embedding subtitles into videos.
    """

    @staticmethod
    def create_video_with_subtitles(
        video_path: str,
        srt_path: str,
        appearance: AppearanceType,
        output_path: str,
    ) -> None:
        """
        Create a video with embedded subtitles.
        """

        match appearance:
            case AppearanceType.OUTLINE:
                extra_style = "BorderStyle=1,Outline=2,"
            case AppearanceType.BLACK:
                extra_style = "BorderStyle=3,BackColour=&H80000000"
            case AppearanceType.TRANSPARENT:
                extra_style = "BorderStyle=1,Outline=0,"
            case _:
                raise EmbeddingSubtitlesException(message="Unsupported appearance type")

        force_style = (
            f"FontName=Intro Bold,FontSize=20,Alignment=2,MarginV=40,Shadow=0,{extra_style}"
        )

        vf_filter = f"subtitles={srt_path}:fontsdir=./fonts:force_style='{force_style}'"

        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vf",
            vf_filter,
            "-c:v",
            "libx264",
            "-crf",
            "20",
            "-preset",
            "medium",
            "-c:a",
            "copy",
            output_path,
        ]

        try:
            log.debug("Running ffmpeg command", command=" ".join(command))
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            log.debug("ffmpeg command completed", command=" ".join(command))
        except subprocess.CalledProcessError as e:
            raise EmbeddingSubtitlesException(message="Failed to embed subtitles into video") from e

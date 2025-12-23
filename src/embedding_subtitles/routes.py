from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from src.config import settings
from src.embedding_subtitles.dependencies import EmbeddingSubtitlesServiceDep
from src.embedding_subtitles.enums import AppearanceType
from src.embedding_subtitles.exceptions import EmbeddingSubtitlesException
from src.utils import cleanup_files, generate_uuid

router = APIRouter(tags=["Embedding Subtitles"])


@router.post(
    "/embed_subtitles",
    summary="Embed Subtitles",
    description="""
        Embed subtitles into a video file.
    """,
    response_class=FileResponse,
    responses={
        200: {
            "description": "Video file with embedded subtitles",
        },
    },
)
async def embed_subtitles(
    video: Annotated[UploadFile, File(..., description="Upload video file (.mp4)")],
    srt: Annotated[UploadFile, File(..., description="Upload srt file (.srt)")],
    appearance: Annotated[
        AppearanceType,
        Form(
            ...,
            description="Appearance type for subtitles: OUTLINE, BLACK, TRANSPARENT",
        ),
    ],
    embedding_subtitles_service: EmbeddingSubtitlesServiceDep,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    """
    Endpoint to embed subtitles into a video file.
    """

    job_id = generate_uuid()
    video_path = f"{settings.TMP_DIR}/{job_id}_input.mp4"
    srt_path = f"{settings.TMP_DIR}/{job_id}.srt"
    output_path = f"{settings.TMP_DIR}/{job_id}_output.mp4"

    with open(video_path, "wb") as f:
        f.write(await video.read())

    with open(srt_path, "wb") as f:
        f.write(await srt.read())

    try:
        await run_in_threadpool(
            embedding_subtitles_service.create_video_with_subtitles,
            video_path,
            srt_path,
            appearance,
            output_path,
        )

        background_tasks.add_task(
            cleanup_files,
            video_path,
            srt_path,
            output_path,
        )

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename=(
                f"{video.filename}_with_subtitles.mp4"
                if video.filename
                else "output_with_subtitles.mp4"
            ),
        )
    except EmbeddingSubtitlesException as e:
        cleanup_files(video_path, srt_path, output_path)
        raise e

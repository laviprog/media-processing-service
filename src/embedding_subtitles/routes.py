import asyncio
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from src.config import settings
from src.embedding_subtitles.dependencies import EmbeddingSubtitlesServiceDep
from src.embedding_subtitles.enums import AppearanceType
from src.embedding_subtitles.exceptions import EmbeddingSubtitlesException
from src.utils import cleanup_files, generate_uuid

router = APIRouter(tags=["Embedding Subtitles"])


embedding_subtitles_semaphore = asyncio.Semaphore(2)


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
) -> FileResponse:
    """
    Endpoint to embed subtitles into a video file.
    """

    # Validate file types
    if video.content_type not in ["video/mp4", "application/octet-stream"]:
        raise HTTPException(status_code=400, detail="Video file must be MP4 format")

    if srt.content_type not in ["application/x-subrip", "text/plain", "application/octet-stream"]:
        raise HTTPException(status_code=400, detail="Subtitle file must be SRT format")

    job_id = generate_uuid()
    video_path = f"{settings.TMP_DIR}/{job_id}_input.mp4"
    srt_path = f"{settings.TMP_DIR}/{job_id}.srt"
    output_path = f"{settings.TMP_DIR}/{job_id}_output.mp4"

    # Track which files were created for cleanup
    created_files = []

    try:
        # Save uploaded video
        with open(video_path, "wb") as f:
            f.write(await video.read())
        created_files.append(video_path)

        # Save uploaded srt
        with open(srt_path, "wb") as f:
            f.write(await srt.read())
        created_files.append(srt_path)

        async with embedding_subtitles_semaphore:
            await run_in_threadpool(
                embedding_subtitles_service.create_video_with_subtitles,
                video_path,
                srt_path,
                appearance,
                output_path,
            )
        created_files.append(output_path)

        # Clean up input files immediately
        cleanup_files(video_path, srt_path)

        # Return response with background cleanup for output file
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename=(
                f"{video.filename.rsplit('.', 1)[0]}_with_subtitles.mp4"
                if video.filename
                else "output_with_subtitles.mp4"
            ),
            background=BackgroundTask(cleanup_files, output_path),
        )

    except EmbeddingSubtitlesException as e:
        cleanup_files(*created_files)
        raise e

    except Exception as e:
        cleanup_files(*created_files)
        raise HTTPException(status_code=500, detail="Failed to process video") from e

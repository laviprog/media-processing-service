from functools import lru_cache
from typing import Annotated, TypeAlias

from fastapi import Depends

from src.embedding_subtitles.service import EmbeddingSubtitlesService


@lru_cache
def provide_embedding_subtitles_service() -> EmbeddingSubtitlesService:
    return EmbeddingSubtitlesService()


EmbeddingSubtitlesServiceDep: TypeAlias = Annotated[
    EmbeddingSubtitlesService, Depends(provide_embedding_subtitles_service)
]

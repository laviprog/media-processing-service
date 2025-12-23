class EmbeddingSubtitlesException(Exception):
    """Base exception for embedding subtitles errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

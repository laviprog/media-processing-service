import os
import uuid


def generate_uuid() -> str:
    """
    Generate a unique UUID4 string.
    """
    return str(uuid.uuid4())


def cleanup_files(*paths: str) -> None:
    """
    Remove files at the specified paths if they exist.
    """
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

from datetime import datetime
from pydantic import BaseModel


class FileMetadata(BaseModel):
    """metadata describing a file"""

    filename: str
    relative_path: str
    absolute_path: str
    extension: str
    size_bytes: int
    last_modified: datetime

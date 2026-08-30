"""This file holds the small pieces every loader in this folder shares.

That is the shape each loader hands back after reading a file, plus two
small helpers so we do not repeat the same checks in every single loader.
"""

from dataclasses import dataclass, field
from pathlib import Path

import logfire

# if a file is bigger than this we stop instead of trying to read the whole
# thing into memory. nothing in our real data comes close to this size, so
# this only kicks in if something unusual gets fed to a loader by mistake.
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024


@dataclass
class LoadedDocument:
    """This is what every loader in this folder hands back.

    text is the words we pulled out of the file.
    source is the file path, so later we know which file an answer came from.
    metadata is anything extra the loader learned, like the file type or how
    many pages or slides it had.
    """

    text: str
    source: str
    metadata: dict = field(default_factory=dict)


def check_file_size(file_path: Path) -> None:
    """Look at how big a file is before we try to read it.

    If it is bigger than MAX_FILE_SIZE_BYTES we raise an error right away
    instead of letting a huge file freeze the whole ingestion job.
    """
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"{file_path} is {size / 1_000_000:.1f} mb, which is over the "
            f"{MAX_FILE_SIZE_BYTES / 1_000_000:.0f} mb limit for one file"
        )


def warn_if_empty(text: str, file_path: Path) -> None:
    """Check if we ended up with no real text after reading a file.

    An empty result usually means something went wrong. Maybe it is a
    scanned pdf with no real text in it, or a slide where all the words sit
    inside a picture we cannot read. This does not stop anything, it just
    leaves a clear note in the logs so it does not go unnoticed later.
    """
    if not text or not text.strip():
        logfire.warning("no text came out of this file", file=str(file_path))

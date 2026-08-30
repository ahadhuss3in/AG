"""This file is for plain text files, the ones ending in .txt.

There is nothing fancy to strip out here. A text file is already just
words, so all we do is open it, work out what encoding it was saved with,
and read it.
"""

from pathlib import Path

import logfire
from bs4 import UnicodeDammit

from . import LoadedDocument, check_file_size, warn_if_empty


def load(file_path: str | Path) -> LoadedDocument:
    """Open a text file and read whatever is inside it."""
    file_path = Path(file_path)

    with logfire.span("load_text", file=str(file_path)):
        try:
            check_file_size(file_path)

            # we read the file as raw bytes first because we do not always
            # know what encoding it was saved with. some older files use
            # something other than utf-8, and just guessing utf-8 can turn
            # real letters into broken symbols. UnicodeDammit looks at the
            # bytes and works out the real encoding for us.
            raw_bytes = file_path.read_bytes()
            text = UnicodeDammit(raw_bytes).unicode_markup
        except Exception:
            logfire.exception("could not read this text file", file=str(file_path))
            raise

        warn_if_empty(text, file_path)

        logfire.info("read text file", file=str(file_path), chars=len(text))

        return LoadedDocument(
            text=text,
            source=str(file_path),
            metadata={"file_type": "text"},
        )

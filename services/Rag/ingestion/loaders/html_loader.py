"""This file is for html files
using trafilatura to pull out the readable content and metadata.
since majority of it will be bs like ads etc.
"""

import json
from pathlib import Path

import logfire
import trafilatura
from bs4 import BeautifulSoup, UnicodeDammit

from . import LoadedDocument, check_file_size, warn_if_empty


def loadhtml(file_path: str | Path) -> LoadedDocument:
    """Reads an html file and pull out the readable content."""
    file_path = Path(file_path)

    with logfire.span("load_html", file=str(file_path)):
        try:
            check_file_size(file_path)
            raw_bytes = file_path.read_bytes()

            # trafilatura can read the raw bytes itself and figure out the
            # encoding on its own, so we do not need to decode it by hand
            # first. it also drops most menus, footers, and other clutter
            # for us automatically.
            result = trafilatura.extract(
                raw_bytes, output_format="json", with_metadata=True
            )

            if result:
                data = json.loads(result)
                text = data.get("text") or ""
                title = data.get("title")
                author = data.get("author")
            else:
                # if its a small html file with no real content, trafilatura will return None
                # hence we use beautifulsop to extract the other part as fall back
                ### FALLBACK ###

                html = UnicodeDammit(raw_bytes).unicode_markup
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
                title = soup.title.string.strip() if soup.title and soup.title.string else None
                author = None
        except Exception:
            logfire.exception("could not read this html file", file=str(file_path))
            raise

        warn_if_empty(text, file_path)


## common for all to log and return the loaded document
        logfire.info(
            "read html file",
            file=str(file_path),
            chars=len(text),
            title=title,
        )

        return LoadedDocument(
            text=text,
            source=str(file_path),
            metadata={"file_type": "html", "title": title, "author": author},
        )

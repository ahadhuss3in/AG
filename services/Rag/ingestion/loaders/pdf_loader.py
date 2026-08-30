"""This file is for pdf files, the ones ending in .pdf.

We use a library called pdfplumber instead of the more basic pypdf, because
it keeps the reading order of the page more sensible. That matters a lot
for the papers in this project, since many of them are written in two
columns, and a simpler reader would mix the columns together.
"""

from pathlib import Path

import logfire
import pdfplumber

from . import LoadedDocument, check_file_size, warn_if_empty


def _format_table(rows: list[list[str | None]]) -> str:
    """Turn a table's rows into plain text, one row per line.
    """
    lines = []
    for row in rows:
        cells = [cell if cell is not None else "" for cell in row]
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def load(file_path: str | Path) -> LoadedDocument:
    """Read a pdf file page by page and pull out its text and tables.

    If a page has no text at all, we still keep going, but we leave a
    warning behind. If every single page turns out empty, that usually
    means the pdf is just scanned pictures of pages with no real text
    layer, and reading it properly later would need something like ocr,
    which this loader does not do yet.
    """
    file_path = Path(file_path)

    with logfire.span("load_pdf", file=str(file_path)):
        try:
            check_file_size(file_path)

            pages_text = []
            empty_pages = 0

            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page_number, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if not page_text:
                        logfire.warning(
                            "pdf page had no extractable text",
                            file=str(file_path),
                            page=page_number,
                        )
                        page_text = ""
                        empty_pages += 1

                    page_block = f"[page {page_number}]\n{page_text}"

                    # a table's words already show up in page_text above,
                    # but jumbled together since a flat text reader does not
                    # know where the rows and columns are. here we pull the
                    # same tables out again in a cleaner row by row shape
                    # and add that on too, so the real structure is not lost.
                    for table_index, table_rows in enumerate(
                        page.extract_tables(), start=1
                    ):
                        table_text = _format_table(table_rows)
                        if table_text.strip():
                            page_block += (
                                f"\n[page {page_number} table {table_index}]\n"
                                f"{table_text}"
                            )

                    pages_text.append(page_block)

            text = "\n\n".join(pages_text)

            if page_count and empty_pages == page_count:
                logfire.warning(
                    "every page in this pdf had no text, it is likely a "
                    "scanned document with no text layer",
                    file=str(file_path),
                    pages=page_count,
                )
        except Exception:
            logfire.exception("could not read this pdf file", file=str(file_path))
            raise

        warn_if_empty(text, file_path)

        logfire.info(
            "read pdf file",
            file=str(file_path),
            pages=page_count,
            empty_pages=empty_pages,
            chars=len(text),
        )

        return LoadedDocument(
            text=text,
            source=str(file_path),
            metadata={"file_type": "pdf", "page_count": page_count},
        )

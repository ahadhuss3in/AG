from typing import List
import logfire


def _split_oversized(text: str, chunk_size: int) -> List[str]:
    """Break one piece of text that is already bigger than chunk_size into
    smaller pieces, splitting on whitespace so words don't get cut in half.
    """
    words = text.split()
    pieces = []
    current = ""
    for word in words:
        candidate = f"{current} {word}" if current else word
        if len(candidate) > chunk_size and current:
            pieces.append(current)
            current = word
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def chunk_text(text:str, chunk_size:int = 1500) -> List[str]:
    """Simple chnker that splits the words by paragraphs.
        Ensures chunks do not exceed the specified size.
    """
    with logfire.span("Text chunking", text_length = len(text)):
        if not text.strip():
            return[]
        paragraphs = text.split("\n\n")

        # a paragraph can already be bigger than chunk_size on its own, for
        # example a whole pdf page with no blank lines in it at all. break
        # those down first, so nothing bigger than chunk_size ever reaches
        # the packing loop below.
        pieces = []
        for p in paragraphs:
            if len(p) > chunk_size:
                pieces.extend(_split_oversized(p, chunk_size))
            else:
                pieces.append(p)

        chunks=[]
        current_chunk=""

        for p in pieces:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        valid_chunks = [c for c in chunks if c.strip()]
        logfire.info(f"Generated {len(valid_chunks)} chunks")
        return valid_chunks
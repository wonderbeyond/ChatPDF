def make_chunks(text, chunk_size: int, overlap: int = 0):
    """Split text into chunks with overlap."""
    chunks = []
    len_ = len(text)
    for i in range(0, len_, chunk_size - overlap):
        chunks.append(text[i: i + chunk_size])
        if i + chunk_size >= len_:
            break
    return chunks


if __name__ == "__main__":
    assert make_chunks("abcd", chunk_size=2) == ["ab", "cd"]

    assert make_chunks("abcde", chunk_size=2) == ["ab", "cd", "e"]

    assert make_chunks(
        "The weather is lovely today.",
        chunk_size=8,
        overlap=3,
    ) == [
        "The weat", "eather i", "r is lov", "lovely t", "y today."
    ]

    assert make_chunks("Are you OK?", chunk_size=8, overlap=3) == [
        "Are you ", "ou OK?"
    ]

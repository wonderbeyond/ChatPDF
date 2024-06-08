import logging

from chatpdf.llm_client import default_client
from chatpdf.utils.chunking import make_chunks
from chatpdf.datatypes import Message
from chatpdf.conf import settings
from chatpdf.caches import cache_by_args

logger = logging.getLogger(__name__)


@cache_by_args(timeout=3600)
def _summarize_piece(piece: str) -> str:
    """Summarize chunked text."""
    return default_client.complete(
        [
            Message(
                role="system",
                content=(
                    "You will be provided with a piece of text enclosed in triple quotes. "
                    "Summarize the text in about 150 words."
                ),
            ),
            Message(role="user", content=f'"""{piece}"""'),
        ]
    )[0].content


@cache_by_args(timeout=300)
def summarize_article(article: str) -> str:
    """Summarize an article via LLM API."""
    chunk_size = settings["chunk_size_for_summary"]
    overlay = settings["chunk_size_for_summary_overlay"]
    summaries = []

    for idx, pcs in enumerate(
        make_chunks(article, chunk_size=chunk_size, overlap=overlay)
    ):
        logger.info(f"Summarizing chunk {idx}...")
        summaries.append(_summarize_piece(pcs))

    logger.info("Making final summary...")
    final_summary = default_client.complete(
        [
            Message(
                role="system",
                content=(
                    "You will be provided with a batch of summaries "
                    "enclosed in triple quotes. "
                    "each summary is generated from a chunk of the same article. "
                    "Please generate a final summary for the article in about 150 words."
                ),
            ),
            Message(
                role="user",
                content="\n".join([f'"""{s}"""' for s in summaries]),
            ),
        ]
    )[0].content

    return final_summary


if __name__ == "__main__":
    from chatpdf.utils.pdf import extract_text_from_pdf

    logging.basicConfig(level=logging.INFO)

    s = summarize_article(
        extract_text_from_pdf(
            # "/Users/wonder/Downloads/后端面试题(远程pre-interview).pdf"
            "/Users/wonder/Downloads/handbook.pdf"
        )
    )
    print(s)

from typing import Optional, IO
import dataclasses as dc
import os.path as op
from uuid import uuid4
import hashlib

import numpy as np
import cloudpickle

from chatpdf.datatypes import Message
from chatpdf.utils.pdf import extract_text_from_pdf
from chatpdf.summarizing import summarize_article
from chatpdf.embedding import get_embeddings, semantic_search
from chatpdf.llm_client import default_client as llm_client
from chatpdf.conf import settings
from chatpdf.utils.chunking import make_chunks
from chatpdf.caches import default_cache as cache


@dc.dataclass
class PDFInfo:
    filename: str
    text: str
    summary: Optional[str]

    @property
    def content_hash(self):
        return hashlib.md5(self.text.encode()).hexdigest()


@dc.dataclass
class CorpusEntry:
    index: int
    text: str
    embedding: np.ndarray


class Chat:
    """
    A Chat represents a conversation, which has a bound PDF and some talking history.
    """
    id: str
    pdf_info: Optional[PDFInfo]
    messages: list[Message]
    corpus: Optional[list[CorpusEntry]]
    memoized_messages: int = 6

    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid4())
        self.pdf_info = None
        self.messages = []
        self.corpus = None

    def save(self):
        pass

    @classmethod
    def load(cls, id: str):
        pass

    def bind_pdf(self, pdf: IO, filename=None) -> None:
        article = extract_text_from_pdf(pdf)
        summary = summarize_article(article)
        self.pdf_info = PDFInfo(
            filename=op.basename(filename or pdf.name),
            text=article,
            summary=summary,
        )

    def make_corpus(self) -> None:
        """Make corpus (with embeddings) from PDF text."""
        if not self.pdf_info:
            raise RuntimeError("PDF not bound yet!")

        cache_key = f"pdf-corpus-{self.pdf_info.content_hash}"

        if cached := cache.get(cache_key):
            self.corpus = cloudpickle.loads(cached)
            return

        chunk_size = settings["chunk_size_for_corpus"]
        overlap = settings["chunk_size_for_corpus_overlap"]

        chunks = make_chunks(self.pdf_info.text, chunk_size=chunk_size, overlap=overlap)
        embeddings = get_embeddings(chunks)

        self.corpus = [
            CorpusEntry(index=i, text=txt, embedding=emb)
            for i, (txt, emb) in enumerate(zip(chunks, embeddings))
        ]

        cache.set(cache_key, cloudpickle.dumps(self.corpus), timeout=43200)

    def query_corpus(self, query: str) -> list[CorpusEntry]:
        """Find most relevant entries in corpus for a query."""
        if not self.corpus:
            raise RuntimeError("Corpus not made yet!")

        sims = semantic_search(
            query_embeddings=get_embeddings(query),
            corpus_embeddings=np.array([entry.embedding for entry in self.corpus]),
            top_k=3,
        )[0]
        return [self.corpus[sim["corpus_id"]] for sim in sims]

    def push_message(self, message: Message) -> None:
        """Push a message to the chat, auto remove old messages to keep context size."""
        self.messages.append(message)
        if len(self.messages) > self.memoized_messages:
            self.messages.pop(0)

    def ask(self, question: str) -> list[Message]:
        if not self.pdf_info:
            raise RuntimeError("PDF not bound yet!")

        if not self.corpus:
            self.make_corpus()

        self.push_message(Message(role="user", content=question))
        relevant_corpus = self.query_corpus(question)
        wire_messages = [
            Message(
                role="system",
                content=(
                    "You are a chatbot to answer questions about a PDF file.\n"
                    "If the user ask you a question in Chinese, please reply in Chinese.\n"
                    f"The summary of the PDF content is:\n{self.pdf_info.summary}"
                ),
            ),
            *self.messages,
            Message(
                role="system",
                content=(
                    "Some relevant parts about this user question are listed below "
                    "(each enclosed in triple quotes):\n"
                    + "\n".join([f'"""{e.text}"""' for e in relevant_corpus])
                    + "\nPlease give user a concise answer based on information in this context. "
                    + "If you can't find any exact information, don't make up an answer."
                ),
            ),
        ]
        res_messages = llm_client.complete(wire_messages)

        for m in res_messages:
            self.push_message(m)

        return res_messages


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    chat = Chat()
    with open("/Users/wonder/Downloads/后端面试题(远程pre-interview).pdf", "rb") as f:
        chat.bind_pdf(f)
        assert chat.pdf_info is not None
        assert chat.pdf_info.summary is not None

    chat.make_corpus()
    assert chat.corpus is not None
    assert isinstance(chat.corpus[0].embedding, np.ndarray)

    for q in (
        "完成这个远程面试题目大概需要多长时间?",
        "该公司具有什么优势？",
        "该公司看重候选人的哪些素质？",
    ):
        print(f"Q: {q}")
        answer = chat.ask(q)[0].content
        print(f"A: {answer}")

import functools

import chatpdf

from sentence_transformers import SentenceTransformer
from sentence_transformers import util as st_util

MODEL_PATH = str(chatpdf.PROJECT_ROOT / "hf-models/BAAI/bge-large-zh-v1.5")


@functools.cache
def get_embedding_model(model=MODEL_PATH):
    """Return cached model."""
    return SentenceTransformer(model, local_files_only=True)


def get_embeddings(texts: str | list[str]):
    model = get_embedding_model()
    return model.encode(texts)


def semantic_search(query_embeddings, corpus_embeddings, top_k: int):
    return st_util.semantic_search(
        query_embeddings=query_embeddings,
        corpus_embeddings=corpus_embeddings,
        top_k=top_k,
    )


if __name__ == "__main__":
    corpus = [
        "The weather is lovely today.",

        "You can use the huggingface_hub library to create, delete, "
        "update and retrieve information from repos. You can also "
        "download files from repos or integrate them into your library! "
        "For example, you can quickly load a Scikit-learn model with "
        "a few lines.",

        "提交代码虽然不是必选项，但我们还是建议您考虑提供，"
        "因为这可以帮助我们的技术负责人更全面、更客观地了解您的编码习惯和规范程度。"
        "通过直观的代码审查，我们可以更准确地评估您的技术实力，"
        "为后续的面试环节提供更有针对性的参考。这不仅能让我们的判断更加深入和准确，"
        "也可以节省双方宝贵的时间，提高面试效率。",

        "在进行本次面试题目的评估时，我们将依据以下两个主要维度进行综合评价："
        "完成的功能完整度和远程面试中展现的产品思考能力和学习能力。",
    ]

    model = get_embedding_model()
    embeddings = get_embeddings(corpus)

    for query in [
        "How is the weather today?",
        "今天天气怎么样？",
        "使用huggingface_hub库能够做什么？",
        "我是否应该提交代码？",
        "如何评估面试题目？",
        "How to evaluate this interview questions",
    ]:
        query_embedding = model.encode(query)
        query_result = semantic_search(query_embedding, embeddings, top_k=1)
        print(f"Q: {query}")
        for res in query_result[0]:
            corpus_id = res["corpus_id"]
            score = res["score"]
            print(f"[{score:.2f}] {corpus[corpus_id]}")
        print()  # sep line

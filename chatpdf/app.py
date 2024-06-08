from time import perf_counter

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from chatpdf.chat import Chat

# Keep active chats in memory
chats: dict[str, Chat] = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_access(request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    end_time = perf_counter()
    elapsed_time = end_time - start_time
    print(
        f"""{request.client.host} - "{request.method} {request.url.path}" {response.status_code} Elapsed {elapsed_time:.3f}s"""  # noqa: E501
    )
    return response


@app.post("/chat/")
def new_chat(file: UploadFile):
    """Start new chat from a PDF file."""
    chat = Chat()
    chat.bind_pdf(file.file, filename=file.filename)
    chats[chat.id] = chat
    assert chat.pdf_info is not None
    return {
        "id": chat.id,
        "pdf_info": {
            "filename": chat.pdf_info.filename,
            "summary": chat.pdf_info.summary,
        },
    }


@app.post("/chat/{chat_id}/make_corpus")
def make_corpus(chat_id: str):
    if not (chat := chats.get(chat_id)):
        raise HTTPException(status_code=404, detail=f"Chat not found by ID {chat_id}!")
    chat.make_corpus()
    assert chat.pdf_info is not None
    return {"message": f"Corpus generated for {chat.pdf_info.filename}."}


@app.post("/chat/{chat_id}/ask")
def ask(chat_id: str, question: str):
    if not (chat := chats.get(chat_id)):
        raise HTTPException(status_code=404, detail=f"Chat not found by ID {chat_id}!")
    messages = chat.ask(question)
    return {"messages": messages}


@app.post("/chat/{chat_id}/destroy")
def destroy(chat_id: str):
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail=f"Chat not found by ID {chat_id}!")
    del chats[chat_id]
    return {"message": f"Chat {chat_id} destroyed."}


if __name__ == "__main__":
    import logging

    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    # config root logger
    LOGGING_CONFIG["loggers"].setdefault("", {}).setdefault("level", "INFO")

    uvicorn.run("chatpdf.app:app", reload=True, access_log=False)

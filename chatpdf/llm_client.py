import dataclasses as dc

import httpx

from chatpdf.conf import settings
from chatpdf.datatypes import Message


class OpenRouterClient:
    _base_url = "https://openrouter.ai/api/v1"

    def __init__(self, model: str, api_key: str):
        self._model = model
        self._api_key = api_key

    def complete(self, messages: list[Message]) -> list[Message]:
        resp = httpx.post(
            url=f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [dc.asdict(m) for m in messages],
            })
        resp.raise_for_status()
        return [
            Message(role=c["message"]["role"], content=c["message"]["content"])
            for c in resp.json()["choices"]
        ]


default_client = OpenRouterClient(
    model="mistralai/mistral-7b-instruct",
    api_key=settings["openrouter_api_key"],
)

if __name__ == "__main__":
    res_messages = default_client.complete(
        [Message(role="user", content="How to implement the ChatPDF APP?")]
    )
    print(res_messages[0].content)

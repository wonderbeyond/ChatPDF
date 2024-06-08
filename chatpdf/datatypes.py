"""Shared data types across this project."""

import dataclasses as dc


@dc.dataclass
class Message:
    role: str
    content: str

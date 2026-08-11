"""The interviewee port."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Interviewee(Protocol):
    def answer(self, question: str) -> str:
        """Given the interviewer's question, return this person's answer."""
        ...

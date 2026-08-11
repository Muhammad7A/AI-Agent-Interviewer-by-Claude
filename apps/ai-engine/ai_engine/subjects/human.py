"""A real person answering at the terminal."""
from __future__ import annotations


class HumanInterviewee:
    """Reads the subject's answer from stdin. Used for live fieldwork."""

    def answer(self, question: str) -> str:
        try:
            return input("you> ").strip()
        except EOFError:
            return ""

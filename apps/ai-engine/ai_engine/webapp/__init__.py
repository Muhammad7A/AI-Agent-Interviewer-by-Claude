"""The consultant workspace — a local web app over the existing pipeline.

Deliberately **consultant-only**. The employer never gets a login; they receive a
generated, firewalled document. That keeps the privacy boundary a property of the
architecture rather than a permissions checkbox that a future feature can tick.

The app adds no domain logic. It is a surface over what already exists —
``InterviewDriver``, ``TranscriptStore``, ``EvidenceTagger``, ``ValidationGate``,
``privacy.release`` — so the guarantees it presents are the ones the engine actually
enforces, not a second implementation of them.
"""

from .app import create_app

__all__ = ["create_app"]

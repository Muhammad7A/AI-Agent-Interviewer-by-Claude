"""Content-addressed storage for derived results.

Everything the pipeline computes *from* a transcript — extracted claims, entailment
verdicts, relation classifications — is expensive to produce and cheap to keep. Until
now none of it was kept, so the consultant workspace recomputed the entire pipeline on
every page view: the same 3 stored interviews produced the same 3 model calls on a
refresh, and an engagement report re-ran every pairwise relation call each time it was
opened. With a live model that is minutes of latency and repeated spend per click.

Two properties make caching here correct rather than merely fast:

  * **Transcripts are immutable and finalized.** A derived result is therefore a pure
    function of its inputs, and can never go stale relative to a transcript that
    changed underneath it — because none ever does.
  * **Keys carry the prompt version and the model.** Change either and the key
    changes, so a prompt edit invalidates its own cache automatically rather than
    silently serving results from the previous behaviour.

The contents are testimony — cached extraction output contains verbatim claim
statements — so this is encrypted at rest with the same cipher as everything else. An
unencrypted cache would quietly reintroduce the plaintext leak the event logs just had.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

from .crypto import Cipher, NullCipher

SCHEMA = "ontora.derived/v1"
_PLAIN = ".derived.json"
_ENCRYPTED = ".derived.enc"

#: Cached entries older than this are swept. Bounded so a long-lived engagement does
#: not accumulate every superseded prompt version forever.
DEFAULT_TTL = timedelta(days=30)


def content_key(*parts: object) -> str:
    """A stable key over the inputs that determine a result."""
    material = "\x1f".join(str(p) for p in parts)
    return sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CacheStats:
    hits: int = 0
    misses: int = 0
    writes: int = 0

    @property
    def total(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        return self.hits / self.total if self.total else 0.0


class DerivedStore:
    """Encrypted, expiring, content-addressed cache for derived artifacts."""

    def __init__(self, data_dir: Path | str, cipher: Cipher | None = None) -> None:
        self._dir = Path(data_dir) / "derived"
        self._cipher = cipher or NullCipher()
        from .crypto import assert_encrypted_in_production

        assert_encrypted_in_production(self._cipher, "the derived-result cache")
        self.hits = 0
        self.misses = 0
        self.writes = 0

    @property
    def directory(self) -> Path:
        return self._dir

    @property
    def encrypted(self) -> bool:
        return self._cipher.protects_at_rest

    @property
    def stats(self) -> CacheStats:
        return CacheStats(hits=self.hits, misses=self.misses, writes=self.writes)

    def _path(self, key: str) -> Path:
        # Keys are hex digests, so this cannot escape the directory; validated anyway
        # because a caller could pass something else.
        if not key or not all(c in "0123456789abcdef" for c in key):
            raise ValueError("cache key must be a hex digest")
        return self._dir / f"{key}{_ENCRYPTED if self.encrypted else _PLAIN}"

    def get(self, key: str) -> dict | None:
        for suffix, encrypted in ((_ENCRYPTED, True), (_PLAIN, False)):
            path = self._dir / f"{key}{suffix}"
            if not path.exists():
                continue
            try:
                blob = path.read_bytes()
                raw = self._cipher.decrypt(blob) if encrypted else blob
                record = json.loads(raw.decode("utf-8"))
                if record.get("schema") != SCHEMA:
                    return None
                self.hits += 1
                return record.get("value")
            except Exception:
                # A corrupt or undecryptable entry is a miss, never a crash: the cache
                # is an optimisation and must never be able to break the pipeline.
                return None
        self.misses += 1
        return None

    def put(self, key: str, value: dict) -> Path:
        record = {
            "schema": SCHEMA,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "value": value,
        }
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._path(key)
        path.write_bytes(self._cipher.encrypt(
            json.dumps(record, ensure_ascii=False).encode("utf-8")))
        self.writes += 1
        return path

    def clear(self) -> int:
        if not self._dir.exists():
            return 0
        removed = 0
        for path in list(self._dir.iterdir()):
            if path.name.endswith((_ENCRYPTED, _PLAIN)):
                path.unlink()
                removed += 1
        return removed

    def sweep(self, ttl: timedelta = DEFAULT_TTL, now: datetime | None = None) -> int:
        """Drop entries older than ``ttl`` — typically superseded prompt versions."""
        if not self._dir.exists():
            return 0
        now = now or datetime.now(timezone.utc)
        removed = 0
        for path in list(self._dir.iterdir()):
            if not path.name.endswith((_ENCRYPTED, _PLAIN)):
                continue
            try:
                blob = path.read_bytes()
                raw = (self._cipher.decrypt(blob)
                       if path.name.endswith(_ENCRYPTED) else blob)
                stored_at = datetime.fromisoformat(
                    json.loads(raw.decode("utf-8"))["stored_at"])
            except Exception:
                path.unlink()      # unreadable entries are not worth keeping
                removed += 1
                continue
            if (now - stored_at) > ttl:
                path.unlink()
                removed += 1
        return removed

"""Report persistence — under the same at-rest policy as the testimony it quotes.

A rendered report is not a derived, safe artifact: it embeds verbatim evidence
quotes, and the org report carries per-participant statements. Writing it as
plaintext while the transcript, event logs, and caches are encrypted protected the
tidiest copies of the sensitive material and left the untidiest one exposed — a
backup of ``data/`` would exfiltrate in plaintext exactly what everything else
guards. So reports go through the same cipher everything else does: encrypted when
a storage key is configured, plaintext only in development.
"""
from __future__ import annotations

from pathlib import Path

from .crypto import Cipher, NullCipher

_PLAIN_SUFFIX = ".md"
_ENCRYPTED_SUFFIX = ".md.enc"


def _validate_stem(stem: str) -> None:
    """A report stem becomes a filename, so it obeys the same rule as every id.

    Today's stems are minted internally (a transcript id, an argparse ``choices``
    value), so this is not reachable — but it is the only path in the package that
    builds a filename from a caller-supplied string without checking it, and the
    asymmetry is exactly how the transcript store ended up as the one that skipped
    the check.
    """
    if not stem or "/" in stem or "\\" in stem or stem.startswith("."):
        raise ValueError(f"invalid report stem: {stem!r}")


def report_path(data_dir: Path, stem: str, *, cipher: Cipher | None = None) -> Path:
    """The path a report with this stem will be written to."""
    _validate_stem(stem)
    effective = cipher or NullCipher()
    suffix = _ENCRYPTED_SUFFIX if effective.protects_at_rest else _PLAIN_SUFFIX
    return Path(data_dir) / f"{stem}{suffix}"


def save_report(data_dir: Path, stem: str, text: str,
                cipher: Cipher | None = None) -> Path:
    """Write a report, encrypted at rest when a real cipher is configured."""
    effective = cipher or NullCipher()
    path = report_path(data_dir, stem, cipher=effective)
    path.parent.mkdir(parents=True, exist_ok=True)
    if effective.protects_at_rest:
        path.write_bytes(effective.encrypt(text.encode("utf-8")))
    else:
        path.write_text(text, encoding="utf-8")
    return path


def load_report(path: Path, cipher: Cipher | None = None) -> str:
    """Read a report in whichever form it is on disk."""
    path = Path(path)
    blob = path.read_bytes()
    if path.name.endswith(_ENCRYPTED_SUFFIX):
        effective = cipher or NullCipher()
        if not effective.protects_at_rest:
            raise ValueError(
                f"{path.name} is encrypted but no storage key is configured")
        return effective.decrypt(blob).decode("utf-8")
    return blob.decode("utf-8")

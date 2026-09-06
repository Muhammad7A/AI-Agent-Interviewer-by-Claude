"""Encryption at rest for stored testimony — as a seam, not as hand-rolled crypto.

Stored transcripts are the most sensitive artifact the system produces: verbatim,
attributable employee testimony including criticism of named managers. Leaving it in
plaintext on disk defeats the privacy firewall as surely as printing it in a report.

Two deliberate decisions:

  * **No cipher is implemented here.** Writing one's own authenticated encryption is
    a reliable way to produce something that looks encrypted and is not. This module
    defines a port and adapts a real library (``cryptography``'s Fernet: AES-128-CBC
    plus HMAC-SHA256) when it is installed via the ``secure`` extra.
  * **Plaintext is available but cannot be used in production.** Local development
    needs readable files; a deployment must not have them. ``NullCipher`` reports
    ``protects_at_rest = False``, and ``Settings.assert_deployable`` refuses to start
    a production runtime with it (see ``ai_engine/config.py``).
"""
from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

KEY_ENV = "GROUNDWORK_STORE_KEY"


class CipherUnavailable(RuntimeError):
    """Raised when a real cipher is required but cannot be constructed."""


def _import_fernet():
    """Import Fernet, or raise :class:`CipherUnavailable`.

    Catches ``BaseException`` deliberately: a broken native build of
    ``cryptography`` does not raise ``ImportError`` — it raises a Rust
    ``PanicException``, which derives from ``BaseException`` and would otherwise
    take down any process that merely *probed* for the capability. Genuine control
    flow (``KeyboardInterrupt``, ``SystemExit``) is re-raised untouched.
    """
    try:
        from cryptography.fernet import Fernet  # type: ignore

        return Fernet
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as exc:
        raise CipherUnavailable(
            "the 'cryptography' package is not importable in this environment "
            f"({type(exc).__name__}); install the extra with "
            "`pip install -e '.[secure]'`"
        ) from exc


@runtime_checkable
class Cipher(Protocol):
    name: str

    @property
    def protects_at_rest(self) -> bool: ...

    def encrypt(self, plaintext: bytes) -> bytes: ...

    def decrypt(self, blob: bytes) -> bytes: ...


class NullCipher:
    """Stores bytes unchanged. Development only — provides no protection."""

    name = "none (plaintext)"

    @property
    def protects_at_rest(self) -> bool:
        return False

    def encrypt(self, plaintext: bytes) -> bytes:
        return plaintext

    def decrypt(self, blob: bytes) -> bytes:
        return blob


class FernetCipher:
    """Authenticated encryption via ``cryptography``'s Fernet.

    Authenticated matters: it detects tampering. A silently altered transcript would
    corrupt every piece of evidence resolved from it.
    """

    name = "fernet (AES-128-CBC + HMAC-SHA256)"

    def __init__(self, key: str | bytes) -> None:
        Fernet = _import_fernet()
        self._fernet = Fernet(key if isinstance(key, bytes) else key.encode("utf-8"))

    @property
    def protects_at_rest(self) -> bool:
        return True

    def encrypt(self, plaintext: bytes) -> bytes:
        return self._fernet.encrypt(plaintext)

    def decrypt(self, blob: bytes) -> bytes:
        return self._fernet.decrypt(blob)


def generate_key() -> str:
    """A fresh Fernet key. Store it in a secret manager, not in the repo."""
    return _import_fernet().generate_key().decode("ascii")


def cipher_available() -> bool:
    """Whether a real cipher can actually be constructed in this environment.

    A probe, so it reports rather than raises — but it probes by *importing*, since
    a package that is installed yet unimportable is exactly the dangerous case: it
    would otherwise read as "encryption available" right up to the first write.
    """
    try:
        _import_fernet()
    except CipherUnavailable:
        return False
    return True


def make_cipher(key: str | None = None) -> Cipher:
    """A real cipher when a key is configured, otherwise plaintext.

    Never silently downgrades a *configured* key: if a key is present but the cipher
    cannot be built, that raises rather than quietly writing plaintext.
    """
    key = key if key is not None else os.environ.get(KEY_ENV)
    if not key:
        return NullCipher()
    return FernetCipher(key)


def assert_encrypted_in_production(cipher: Cipher, what: str) -> None:
    """Refuse a plaintext store when ``GROUNDWORK_ENV=production``.

    Called by every store that persists testimony-derived material, so the
    at-rest guarantee holds at the persistence layer and not only at whatever
    entry point remembered to call ``Settings.assert_deployable``. Deferred
    import: ``config`` imports this package, so a module-level import would be
    circular; the env parse stays single-homed in config.
    """
    from ..config import Runtime, runtime_from_env

    if runtime_from_env() is Runtime.PRODUCTION and not cipher.protects_at_rest:
        raise RuntimeError(
            f"{what} would be written in plaintext, but GROUNDWORK_ENV=production "
            f"requires encryption at rest. Set {KEY_ENV} (and install the "
            f"'secure' extra) before serving real interviews.")

"""Run the consultant workspace.

    python -m ai_engine.webapp                 # http://127.0.0.1:8000
    python -m ai_engine.webapp --port 9000

Binds to localhost by default and on purpose: there is no authentication, so the app
must not be reachable from the network. Binding elsewhere requires --host and prints a
warning, because an unauthenticated tool holding employee testimony on an open
interface is the worst possible configuration.
"""
from __future__ import annotations

import argparse
import sys

from ..config import ModelUnavailable, load_settings, preflight_model
from .app import create_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora consultant workspace")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    settings = load_settings()
    # Prove the configured model answers before anyone schedules an interview
    # against this server — no-op in mock mode. A bad ONTORA_MODEL otherwise
    # surfaces at the participant's first question, where they can do nothing.
    try:
        preflight_model(settings)
    except ModelUnavailable as exc:
        print(f"# {exc}", file=sys.stderr)
        return 1
    print(f"# Ontora consultant workspace — {settings.posture_banner()}")
    print(f"#   data dir: {settings.data_dir}")
    print("#   no authentication: single-consultant local tool")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"#   ⚠ binding to {args.host}: this app has NO authentication and holds "
              f"employee testimony. Do not expose it to a network.")
    print(f"#   → http://{args.host}:{args.port}")

    try:
        import uvicorn
    except ImportError:
        print("uvicorn is not installed. Install the web extra: "
              "pip install -e '.[web]'", file=sys.stderr)
        return 1

    uvicorn.run(create_app(settings), host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Run the employee interview surface.

    python -m ai_engine.employee                 # http://127.0.0.1:8100

Runs on a different port from the consultant workspace because it is a different
application with a different audience. Only this one should ever be reachable by the
people being interviewed.
"""
from __future__ import annotations

import argparse
import sys

from ..config import load_settings
from .app import create_employee_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora employee interview surface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8100)
    args = parser.parse_args(argv)

    settings = load_settings()
    print(f"# Ontora interview surface — {settings.posture_banner()}")
    print(f"#   data dir: {settings.data_dir}")
    print("#   append-only: this app cannot read any interview or reach the workspace")
    print("#   participants reach it at /i/<invitation token>")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(f"#   ⚠ binding to {args.host}: invitation tokens are the only access "
              f"control. Serve over HTTPS and treat the links as secrets.")
    print(f"#   → http://{args.host}:{args.port}")

    try:
        import uvicorn
    except ImportError:
        print("uvicorn is not installed. Install the web extra: "
              "pip install -e '.[web]'", file=sys.stderr)
        return 1

    uvicorn.run(create_employee_app(settings), host=args.host, port=args.port,
                log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())

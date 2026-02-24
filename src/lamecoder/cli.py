from __future__ import annotations

import argparse
import socket
import sys

import uvicorn

from .server import create_app


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser(prog="lamecoder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ui = sub.add_parser("ui", help="Start the local web UI")
    ui.add_argument("--host", default="127.0.0.1")
    ui.add_argument("--port", type=int, default=0)
    ui.add_argument("--reload", action="store_true", help="Auto-reload on code changes")

    args = parser.parse_args(argv)

    if args.cmd == "ui":
        port = args.port if args.port != 0 else _pick_free_port()
        url = f"http://{args.host}:{port}"
        print(f"LameCoder UI: {url}")
        app = create_app()
        uvicorn.run(app, host=args.host, port=port, reload=args.reload, log_level="info")
        return 0

    return 1

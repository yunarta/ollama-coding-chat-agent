from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Dict

from . import store


def _resolve_in_workspace(rel_path: str) -> Path:
    root = store.workspace_root()
    raw = (rel_path or "").strip()
    if not raw:
        raise ValueError("path is required")
    p = Path(raw)
    if p.is_absolute():
        raise ValueError("absolute path is not allowed")

    target = (root / p).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes workspace") from exc
    return target


def tool_read_file(path: str) -> Dict[str, str]:
    target = _resolve_in_workspace(path)
    if not target.exists():
        raise FileNotFoundError(f"not found: {path}")
    if target.is_dir():
        raise IsADirectoryError(f"path is a directory: {path}")
    content = target.read_text(encoding="utf-8")
    return {"tool": "read_file", "path": path, "content": content}


def tool_write_file(path: str, content: str) -> Dict[str, str]:
    target = _resolve_in_workspace(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {
        "tool": "write_file",
        "path": path,
        "bytes": str(len(content.encode("utf-8"))),
    }


def tool_exec_shell(command: str, timeout_s: int = 20) -> Dict[str, str]:
    cmd = (command or "").strip()
    if not cmd:
        raise ValueError("command is required")

    root = store.workspace_root()
    proc = subprocess.run(
        ["bash", "-lc", cmd],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    return {
        "tool": "exec_shell",
        "command": cmd,
        "exit_code": str(proc.returncode),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def parse_tool_command(text: str) -> Dict[str, str] | None:
    raw = (text or "").strip()
    if not raw.startswith("/"):
        return None

    parts = shlex.split(raw)
    if not parts:
        return None

    name = parts[0].lower()
    if name == "/read":
        if len(parts) != 2:
            raise ValueError("usage: /read <relative-path>")
        return tool_read_file(parts[1])

    if name == "/write":
        if len(parts) < 3:
            raise ValueError("usage: /write <relative-path> <content>")
        path = parts[1]
        content = " ".join(parts[2:])
        return tool_write_file(path, content)

    if name == "/sh":
        if len(parts) < 2:
            raise ValueError("usage: /sh <command>")
        command = raw[len(parts[0]) :].strip()
        return tool_exec_shell(command)

    return None


def format_tool_result(result: Dict[str, str]) -> str:
    tool = result.get("tool", "tool")
    if tool == "read_file":
        return f"[tool:read_file]\npath: {result.get('path','')}\n\n{result.get('content','')}"
    if tool == "write_file":
        return (
            f"[tool:write_file]\npath: {result.get('path','')}\n"
            f"bytes_written: {result.get('bytes','0')}"
        )
    if tool == "exec_shell":
        return (
            f"[tool:exec_shell]\ncommand: {result.get('command','')}\n"
            f"exit_code: {result.get('exit_code','')}\n\n"
            f"stdout:\n{result.get('stdout','')}\n"
            f"stderr:\n{result.get('stderr','')}"
        )
    return str(result)

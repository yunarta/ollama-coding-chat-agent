from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, List, Optional

try:
    import fcntl  # type: ignore
except Exception:  # pragma: no cover
    fcntl = None


INDEX_VERSION = 1


def _now_iso() -> str:
    # ISO-ish without timezone; keep it simple and sortable
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def workspace_root() -> Path:
    # By design: workspace is the current directory where lamecoder is executed.
    return Path(os.getcwd()).resolve()


def lame_dir(root: Optional[Path] = None) -> Path:
    root = root or workspace_root()
    return root / ".lame"


def sessions_dir(root: Optional[Path] = None) -> Path:
    return lame_dir(root) / "sessions"


def index_path(root: Optional[Path] = None) -> Path:
    return sessions_dir(root) / "index.json"


def session_path(session_id: str, root: Optional[Path] = None) -> Path:
    return sessions_dir(root) / f"{session_id}.jsonl"


@dataclass
class SessionMeta:
    id: str
    title: str
    created_at: str
    updated_at: str
    snippet: str = ""
    pinned: bool = False


def ensure_storage(root: Optional[Path] = None) -> None:
    d = sessions_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    idx = index_path(root)
    if not idx.exists():
        idx.write_text(json.dumps({"version": INDEX_VERSION, "sessions": []}, indent=2), encoding="utf-8")


@contextmanager
def _locked_open(path: Path, mode: str):
    """Best-effort cross-process file lock.

    On POSIX, uses fcntl.flock. On non-POSIX, it behaves like a normal open.
    This is intentionally simple: stable beats fancy.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open(mode, encoding="utf-8")
    try:
        if fcntl is not None:
            # Exclusive lock is fine for our small files.
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield f
    finally:
        try:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        finally:
            f.close()


def _locked_json_load(path: Path) -> Any:
    with _locked_open(path, "r") as f:
        return json.loads(f.read() or "{}")


def _locked_json_write(path: Path, data: Any) -> None:
    with _locked_open(path, "w") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


def list_sessions(root: Optional[Path] = None) -> List[SessionMeta]:
    root = root or workspace_root()
    ensure_storage(root)
    data = _locked_json_load(index_path(root))
    sessions = [SessionMeta(**s) for s in data.get("sessions", [])]
    # sort: updated desc, then pinned first (stable)
    sessions.sort(key=lambda s: s.updated_at, reverse=True)
    sessions.sort(key=lambda s: not s.pinned)
    return sessions


def _save_sessions(sessions: List[SessionMeta], root: Path) -> None:
    payload = {"version": INDEX_VERSION, "sessions": [asdict(s) for s in sessions]}
    _locked_json_write(index_path(root), payload)


def create_session(title: Optional[str] = None, root: Optional[Path] = None) -> SessionMeta:
    root = root or workspace_root()
    ensure_storage(root)
    sid = uuid.uuid4().hex[:12]
    now = _now_iso()
    meta = SessionMeta(id=sid, title=title or "New Session", created_at=now, updated_at=now, snippet="")

    sessions = list_sessions(root)
    sessions.insert(0, meta)
    _save_sessions(sessions, root)

    # create empty jsonl
    sp = session_path(sid, root)
    sp.touch(exist_ok=True)
    return meta


def rename_session(session_id: str, title: str, root: Optional[Path] = None) -> SessionMeta:
    root = root or workspace_root()
    sessions = list_sessions(root)
    found = None
    for s in sessions:
        if s.id == session_id:
            s.title = title.strip() or s.title
            s.updated_at = _now_iso()
            found = s
            break
    if not found:
        raise KeyError(f"Session not found: {session_id}")
    _save_sessions(sessions, root)
    return found


def pin_session(session_id: str, pinned: bool, root: Optional[Path] = None) -> SessionMeta:
    root = root or workspace_root()
    sessions = list_sessions(root)
    found = None
    for s in sessions:
        if s.id == session_id:
            s.pinned = bool(pinned)
            s.updated_at = _now_iso()
            found = s
            break
    if not found:
        raise KeyError(f"Session not found: {session_id}")
    _save_sessions(sessions, root)
    return found


def read_messages(session_id: str, root: Optional[Path] = None) -> List[dict]:
    root = root or workspace_root()
    sp = session_path(session_id, root)
    if not sp.exists():
        raise KeyError(f"Session not found: {session_id}")

    messages: List[dict] = []
    with _locked_open(sp, "r") as f:
        for line in f.read().splitlines():
            if not line.strip():
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                # tolerate partial corruption; skip bad lines
                continue
    return messages


def append_messages(session_id: str, msgs: Iterable[dict], root: Optional[Path] = None) -> None:
    root = root or workspace_root()
    ensure_storage(root)
    sp = session_path(session_id, root)
    if not sp.exists():
        raise KeyError(f"Session not found: {session_id}")

    msgs_list = list(msgs)

    # append atomically under lock
    with _locked_open(sp, "a") as f:
        for m in msgs_list:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    # update index metadata (updated_at + snippet)
    sessions = list_sessions(root)
    snippet = ""
    last = None
    try:
        # find last user/assistant message among appended
        for m in reversed(msgs_list):
            if m.get("role") in ("user", "assistant") and m.get("content"):
                last = m
                break
        if last:
            snippet = str(last.get("content", ""))[:120].replace("\n", " ")
    except Exception:
        snippet = ""

    now = _now_iso()
    for s in sessions:
        if s.id == session_id:
            s.updated_at = now
            if snippet:
                s.snippet = snippet
            # auto-title from first user message if still default
            if s.title == "New Session":
                # if we appended a user message, use its first line
                for m in msgs_list:
                    if m.get("role") == "user" and m.get("content"):
                        first = str(m["content"]).strip().splitlines()[0][:48]
                        if first:
                            s.title = first
                        break
            break
    _save_sessions(sessions, root)


def new_message(role: str, content: str, *, kind: str = "message") -> dict:
    return {
        "id": uuid.uuid4().hex[:12],
        "role": role,
        "type": kind,
        "content": content,
        "created_at": _now_iso(),
    }

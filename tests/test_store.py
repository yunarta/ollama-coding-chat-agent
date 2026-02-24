import os
from pathlib import Path

from lamecoder import store


def test_session_create_and_append(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    s = store.create_session()
    assert s.id

    store.append_messages(s.id, [store.new_message("user", "hello")])
    msgs = store.read_messages(s.id)
    assert msgs[-1]["role"] == "user"

    sessions = store.list_sessions()
    assert sessions[0].id == s.id
    assert sessions[0].title != ""  # auto-title might kick in


def test_rename_and_pin(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = store.create_session(title="A")
    s2 = store.rename_session(s.id, "B")
    assert s2.title == "B"
    s3 = store.pin_session(s.id, True)
    assert s3.pinned is True

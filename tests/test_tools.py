from __future__ import annotations

import os
from pathlib import Path

import pytest

from lamecoder import tools


def test_read_write_file_roundtrip(tmp_path: Path):
    os.chdir(tmp_path)

    write = tools.tool_write_file("notes/demo.txt", "hello tooling")
    assert write["tool"] == "write_file"

    read = tools.tool_read_file("notes/demo.txt")
    assert read["content"] == "hello tooling"


def test_reject_workspace_escape(tmp_path: Path):
    os.chdir(tmp_path)
    with pytest.raises(ValueError):
        tools.tool_read_file("../etc/passwd")


def test_exec_shell(tmp_path: Path):
    os.chdir(tmp_path)
    out = tools.tool_exec_shell("printf ok")
    assert out["exit_code"] == "0"
    assert out["stdout"] == "ok"


def test_parse_tool_commands(tmp_path: Path):
    os.chdir(tmp_path)

    r = tools.parse_tool_command('/write a.txt "hello world"')
    assert r and r["tool"] == "write_file"

    r2 = tools.parse_tool_command('/read a.txt')
    assert r2 and r2["content"] == "hello world"

    r3 = tools.parse_tool_command('/sh echo hi')
    assert r3 and r3["tool"] == "exec_shell"

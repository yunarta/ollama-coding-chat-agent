from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import store
from . import llm
from . import tools


STATIC_DIR = Path(__file__).parent / "static"


class SessionCreate(BaseModel):
    title: Optional[str] = None


class RenameReq(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class PinReq(BaseModel):
    pinned: bool


class MessageReq(BaseModel):
    content: str = Field(min_length=1)


def create_app() -> FastAPI:
    app = FastAPI(title="lamecoder")

    # Static UI
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    @app.get("/api/health")
    def health() -> Dict[str, Any]:
        return {"ok": True, "workspace": str(store.workspace_root())}

    @app.get("/api/sessions")
    def api_list_sessions() -> Dict[str, Any]:
        try:
            sessions = store.list_sessions()
            return {"sessions": [s.__dict__ for s in sessions]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/sessions")
    def api_create_session(req: SessionCreate) -> Dict[str, Any]:
        try:
            meta = store.create_session(title=req.title)
            return {"session": meta.__dict__}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/sessions/{session_id}")
    def api_get_session(session_id: str) -> Dict[str, Any]:
        try:
            sessions = {s.id: s for s in store.list_sessions()}
            if session_id not in sessions:
                raise HTTPException(status_code=404, detail="session not found")
            msgs = store.read_messages(session_id)
            return {"session": sessions[session_id].__dict__, "messages": msgs}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/sessions/{session_id}/rename")
    def api_rename_session(session_id: str, req: RenameReq) -> Dict[str, Any]:
        try:
            meta = store.rename_session(session_id, req.title)
            return {"session": meta.__dict__}
        except KeyError:
            raise HTTPException(status_code=404, detail="session not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/sessions/{session_id}/pin")
    def api_pin_session(session_id: str, req: PinReq) -> Dict[str, Any]:
        try:
            meta = store.pin_session(session_id, req.pinned)
            return {"session": meta.__dict__}
        except KeyError:
            raise HTTPException(status_code=404, detail="session not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/sessions/{session_id}/messages")
    async def api_post_message(
        session_id: str,
        req: MessageReq,
        stream: bool = Query(default=False),
    ):
        # Append the user message immediately.
        try:
            user_msg = store.new_message("user", req.content)
            store.append_messages(session_id, [user_msg])
        except KeyError:
            raise HTTPException(status_code=404, detail="session not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Built-in tooling commands for read/write/shell.
        try:
            tool_result = tools.parse_tool_command(req.content)
        except Exception as e:
            err_msg = store.new_message("assistant", f"(tool error) {e}")
            store.append_messages(session_id, [err_msg])
            if stream:
                async def tool_err_gen() -> AsyncGenerator[str, None]:
                    yield json.dumps({"type": "done", "assistant": err_msg}, ensure_ascii=False) + "\n"
                return StreamingResponse(tool_err_gen(), media_type="application/x-ndjson")
            return JSONResponse({"user": user_msg, "assistant": err_msg}, status_code=200)

        if tool_result is not None:
            out = tools.format_tool_result(tool_result)
            assistant_msg = store.new_message("assistant", out)
            store.append_messages(session_id, [assistant_msg])
            if stream:
                async def tool_gen() -> AsyncGenerator[str, None]:
                    yield json.dumps({"type": "delta", "content": out}, ensure_ascii=False) + "\n"
                    yield json.dumps({"type": "done", "assistant": assistant_msg}, ensure_ascii=False) + "\n"
                return StreamingResponse(tool_gen(), media_type="application/x-ndjson")
            return JSONResponse({"user": user_msg, "assistant": assistant_msg}, status_code=200)

        # Load full context (simple, stable). Future: compression.
        messages = store.read_messages(session_id)

        system_prompt = (
            "You are LameCoder, a local-first coding agent. "
            "Be concise, propose a plan before risky actions, and respect the workspace boundary. "
            "When user asks read/write/exec actions, mention slash tools: /read /write /sh."
        )

        if not stream:
            try:
                reply = await llm.chat_complete(messages, system_prompt=system_prompt)
                assistant_msg = store.new_message("assistant", reply)
                store.append_messages(session_id, [assistant_msg])
                return JSONResponse({"user": user_msg, "assistant": assistant_msg})
            except Exception as e:
                # persist error as assistant message so the convo isn't mysteriously stuck
                err = f"(error) {e}"
                assistant_msg = store.new_message("assistant", err)
                store.append_messages(session_id, [assistant_msg])
                return JSONResponse({"user": user_msg, "assistant": assistant_msg}, status_code=200)

        async def gen() -> AsyncGenerator[str, None]:
            assistant_text = ""
            try:
                async for delta in llm.chat_stream(messages, system_prompt=system_prompt):
                    assistant_text += delta
                    yield json.dumps({"type": "delta", "content": delta}, ensure_ascii=False) + "\n"
                assistant_msg = store.new_message("assistant", assistant_text)
                store.append_messages(session_id, [assistant_msg])
                yield json.dumps({"type": "done", "assistant": assistant_msg}, ensure_ascii=False) + "\n"
            except Exception as e:
                err = f"(error) {e}"
                assistant_msg = store.new_message("assistant", err)
                store.append_messages(session_id, [assistant_msg])
                yield json.dumps({"type": "done", "assistant": assistant_msg}, ensure_ascii=False) + "\n"

        return StreamingResponse(gen(), media_type="application/x-ndjson")

    return app

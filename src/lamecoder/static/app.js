import { placeholder } from "https://esm.sh/@codemirror/view@6.26.3";
import { EditorView } from "https://esm.sh/@codemirror/view@6.26.3";

const $sessions = document.getElementById("sessions");
const $conversation = document.getElementById("conversation");
const $newBtn = document.getElementById("newSessionBtn");
const $sendBtn = document.getElementById("sendBtn");
const $workspaceInfo = document.getElementById("workspaceInfo");
const $workspaceBanner = document.getElementById("workspaceBanner");
const $thinkingStatus = document.getElementById("thinkingStatus");
const $todoStatus = document.getElementById("todoStatus");

marked.setOptions({ breaks: true });

let state = {
  sessions: [],
  activeSessionId: null,
  messages: [],
};


function setThinkingStatus(text) {
  if ($thinkingStatus) $thinkingStatus.textContent = `Thinking: ${text}`;
}

function setTodoStatus(openCount) {
  if ($todoStatus) $todoStatus.textContent = `Todo: ${openCount} open`;
}

function estimateTodoCount() {
  const pending = state.messages
    .filter((m) => m.role === "assistant")
    .map((m) => m.content || "")
    .join("\n")
    .match(/\b(todo|next|follow-up|follow up|pending)\b/gi);
  return pending ? Math.min(9, pending.length) : 0;
}

function fmtTime(iso) {
  if (!iso) return "";
  return iso.replace("T", " ");
}

function getUrlSession() {
  const p = new URLSearchParams(location.search);
  return p.get("session");
}

function setUrlSession(id) {
  const p = new URLSearchParams(location.search);
  if (id) p.set("session", id);
  history.replaceState(null, "", `${location.pathname}?${p.toString()}`);
}

async function api(path, opts = {}) {
  const r = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!r.ok) {
    let detail = "";
    try { detail = (await r.json()).detail || ""; } catch {}
    throw new Error(`API ${r.status}: ${detail || path}`);
  }
  return r;
}

function draftKey(sessionId) {
  return `lame_draft_${sessionId || "none"}`;
}

function saveDraft() {
  if (!state.activeSessionId) return;
  localStorage.setItem(draftKey(state.activeSessionId), editor.getText());
}

function loadDraft(sessionId) {
  const v = localStorage.getItem(draftKey(sessionId));
  return v || "";
}

function clearDraft(sessionId) {
  localStorage.removeItem(draftKey(sessionId));
}

function renderSessions() {
  $sessions.innerHTML = "";
  for (const s of state.sessions) {
    const el = document.createElement("div");
    el.className = "session-item" + (s.id === state.activeSessionId ? " active" : "");
    el.dataset.sid = s.id;

    const top = document.createElement("div");
    top.className = "session-top";

    const title = document.createElement("div");
    title.className = "session-title";
    title.textContent = (s.pinned ? "📌 " : "") + (s.title || "(untitled)");

    const actions = document.createElement("div");

    const pinBtn = document.createElement("button");
    pinBtn.className = "icon-btn";
    pinBtn.title = s.pinned ? "Unpin" : "Pin";
    pinBtn.textContent = s.pinned ? "📌" : "📍";
    pinBtn.onclick = async (e) => {
      e.stopPropagation();
      await api(`/api/sessions/${s.id}/pin`, { method: "POST", body: JSON.stringify({ pinned: !s.pinned }) });
      await refreshSessions();
    };

    const renameBtn = document.createElement("button");
    renameBtn.className = "icon-btn";
    renameBtn.title = "Rename";
    renameBtn.textContent = "✏️";
    renameBtn.onclick = (e) => {
      e.stopPropagation();
      startInlineRename(el, s);
    };

    actions.appendChild(pinBtn);
    actions.appendChild(renameBtn);

    top.appendChild(title);
    top.appendChild(actions);

    const meta = document.createElement("div");
    meta.className = "session-meta";
    meta.textContent = `${fmtTime(s.updated_at)} • ${s.snippet || ""}`;

    el.appendChild(top);
    el.appendChild(meta);

    el.onclick = async () => {
      await switchSession(s.id);
    };

    $sessions.appendChild(el);
  }
}

function startInlineRename(container, session) {
  const input = document.createElement("input");
  input.className = "inline-edit";
  input.value = session.title || "";
  const titleEl = container.querySelector(".session-title");
  titleEl.textContent = "";
  titleEl.appendChild(input);
  input.focus();
  input.select();

  const finish = async () => {
    const v = input.value.trim();
    if (v && v !== session.title) {
      await api(`/api/sessions/${session.id}/rename`, { method: "POST", body: JSON.stringify({ title: v }) });
    }
    await refreshSessions();
  };

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") finish();
    if (e.key === "Escape") refreshSessions();
  });
  input.addEventListener("blur", finish);
}

function msgEl(msg) {
  const el = document.createElement("div");
  el.className = `msg ${msg.role || ""}`;

  const head = document.createElement("div");
  head.className = "msg-head";

  const badge = document.createElement("div");
  badge.className = "badge";
  badge.textContent = msg.role || "message";

  const time = document.createElement("div");
  time.className = "time";
  time.textContent = fmtTime(msg.created_at);

  head.appendChild(badge);
  head.appendChild(time);

  const body = document.createElement("div");
  body.className = "msg-body";

  // Basic markdown render
  const content = msg.content || "";
  body.innerHTML = marked.parse(content);

  el.appendChild(head);
  el.appendChild(body);

  // Add copy buttons to code blocks
  for (const pre of body.querySelectorAll("pre")) {
    const code = pre.querySelector("code");
    if (!code) continue;

    const bar = document.createElement("div");
    bar.className = "code-toolbar";

    const copy = document.createElement("button");
    copy.className = "btn";
    copy.textContent = "Copy";
    copy.onclick = async () => {
      await navigator.clipboard.writeText(code.innerText);
      copy.textContent = "Copied";
      setTimeout(() => (copy.textContent = "Copy"), 900);
    };

    bar.appendChild(copy);
    pre.parentNode.insertBefore(bar, pre);
  }

  return el;
}

function renderConversation() {
  $conversation.innerHTML = "";
  if (!state.activeSessionId) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.style.maxWidth = "920px";
    empty.style.margin = "0 auto";
    empty.style.padding = "20px";
    empty.textContent = "No session selected. Create one on the left.";
    $conversation.appendChild(empty);
    return;
  }
  for (const m of state.messages) {
    $conversation.appendChild(msgEl(m));
  }
  setTodoStatus(estimateTodoCount());
}

function smartScrollToBottom(force = false) {
  const nearBottom = ($conversation.scrollHeight - $conversation.scrollTop - $conversation.clientHeight) < 120;
  if (force || nearBottom) {
    $conversation.scrollTop = $conversation.scrollHeight;
  }
}

async function refreshSessions() {
  const r = await api("/api/sessions");
  const data = await r.json();
  state.sessions = data.sessions || [];
  renderSessions();
}

async function loadWorkspaceInfo() {
  try {
    const r = await api("/api/health");
    const d = await r.json();
    const info = `workspace: ${d.workspace}`;
    $workspaceInfo.textContent = info;
    if ($workspaceBanner) $workspaceBanner.textContent = info;
  } catch {
    $workspaceInfo.textContent = "";
    if ($workspaceBanner) $workspaceBanner.textContent = "workspace: unavailable";
  }
}

async function switchSession(sessionId) {
  if (state.activeSessionId === sessionId) return;
  // save draft for current
  saveDraft();

  state.activeSessionId = sessionId;
  setUrlSession(sessionId);
  await refreshSessions();
  await loadSession(sessionId);

  // load draft
  editor.setText(loadDraft(sessionId));
}

async function loadSession(sessionId) {
  const r = await api(`/api/sessions/${sessionId}`);
  const data = await r.json();
  state.messages = data.messages || [];
  renderConversation();
  smartScrollToBottom(true);
}

async function createSession() {
  const r = await api("/api/sessions", { method: "POST", body: JSON.stringify({}) });
  const data = await r.json();
  const sid = data.session.id;
  await refreshSessions();
  await switchSession(sid);
}

async function sendMessage() {
  const text = editor.getText().trimEnd();
  if (!text.trim() || !state.activeSessionId) return;

  // optimistic append
  const userMsg = { role: "user", content: text, created_at: new Date().toISOString().slice(0,19) };
  state.messages.push(userMsg);

  const assistantMsg = { role: "assistant", content: "", created_at: new Date().toISOString().slice(0,19) };
  state.messages.push(assistantMsg);

  renderConversation();
  smartScrollToBottom(true);

  // clear editor + draft
  editor.setText("");
  clearDraft(state.activeSessionId);

  // stream response
  $sendBtn.disabled = true;
  $sendBtn.textContent = "...";
  setThinkingStatus("running");

  try {
    const resp = await api(`/api/sessions/${state.activeSessionId}/messages?stream=true`, {
      method: "POST",
      body: JSON.stringify({ content: text }),
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    // Keep a reference to the last assistant message DOM node
    const lastMsgNode = $conversation.querySelectorAll(".msg");
    const assistantNode = lastMsgNode[lastMsgNode.length - 1];
    const assistantBody = assistantNode.querySelector(".msg-body");

    let acc = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.trim()) continue;
        let obj;
        try { obj = JSON.parse(line); } catch { continue; }
        if (obj.type === "delta") {
          acc += obj.content;
          assistantBody.textContent = acc;
          smartScrollToBottom();
        }
        if (obj.type === "done") {
          // Replace with final markdown render
          const final = obj.assistant?.content ?? acc;
          assistantBody.innerHTML = marked.parse(final);
          // add copy buttons for code
          for (const pre of assistantBody.querySelectorAll("pre")) {
            const code = pre.querySelector("code");
            if (!code) continue;
            const bar = document.createElement("div");
            bar.className = "code-toolbar";
            const copy = document.createElement("button");
            copy.className = "btn";
            copy.textContent = "Copy";
            copy.onclick = async () => {
              await navigator.clipboard.writeText(code.innerText);
              copy.textContent = "Copied";
              setTimeout(() => (copy.textContent = "Copy"), 900);
            };
            bar.appendChild(copy);
            pre.parentNode.insertBefore(bar, pre);
          }
          // refresh sessions list (updated snippet/time/title)
          await refreshSessions();
          smartScrollToBottom(true);
          setThinkingStatus("idle");
        }
      }
    }
  } catch (e) {
    // Show error in the last assistant message
    state.messages[state.messages.length - 1].content = `(error) ${e.message || e}`;
    renderConversation();
    setThinkingStatus("error");
  } finally {
    $sendBtn.disabled = false;
    $sendBtn.textContent = "Send";
  }
}

// --- CodeMirror setup ---
const editorTheme = EditorView.theme({
  "&": {
    fontSize: "13px",
    backgroundColor: "transparent",
  },
  ".cm-editor": {
    backgroundColor: "transparent",
  },
  ".cm-content": {
    padding: "12px 12px",
    minHeight: "92px",
    lineHeight: "1.45",
  },
  ".cm-scroller": {
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
    maxHeight: "220px",
    overflow: "auto",
  },
  ".cm-placeholder": {
    color: "#7f91a8",
  },
});

function createFallbackEditor(parent) {
  const ta = document.createElement("textarea");
  ta.className = "editor-fallback";
  ta.placeholder = "Type a message...";
  parent.innerHTML = "";
  parent.appendChild(ta);
  ta.addEventListener("input", () => saveDraft());
  return {
    getText: () => ta.value,
    setText: (v) => { ta.value = v ?? ""; },
  };
}

function createCodeMirrorEditor(parent) {
  const editorView = new EditorView({
    parent,
    doc: "",
    extensions: [
      placeholder("Type a message..."),
      EditorView.lineWrapping,
      editorTheme,
      EditorView.updateListener.of((u) => {
        if (u.docChanged) saveDraft();
      }),
    ],
  });
  return {
    getText: () => editorView.state.doc.toString(),
    setText: (v) => {
      editorView.dispatch({
        changes: { from: 0, to: editorView.state.doc.length, insert: v ?? "" },
      });
    },
  };
}

const editorRoot = document.getElementById("editor");
let editor;
try {
  editor = createCodeMirrorEditor(editorRoot);
} catch (e) {
  console.error("CodeMirror init failed, using textarea fallback:", e);
  editor = createFallbackEditor(editorRoot);
}

// --- Events ---
$newBtn.addEventListener("click", createSession);
$sendBtn.addEventListener("click", sendMessage);

// --- Boot ---
(async function init() {
  setThinkingStatus("idle");
  setTodoStatus(0);
  await loadWorkspaceInfo();
  await refreshSessions();

  const sid = getUrlSession();
  if (sid) {
    try {
      await switchSession(sid);
      return;
    } catch {
      // fallthrough
    }
  }

  if (state.sessions.length) {
    await switchSession(state.sessions[0].id);
  } else {
    await createSession();
  }
})();

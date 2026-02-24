#!/usr/bin/env node
const { chromium } = require("playwright");

async function main() {
  const baseUrl = process.env.UI_BASE_URL || "http://127.0.0.1:8080";
  const prompt = process.env.UI_SMOKE_PROMPT || "Reply exactly OK frontend";
  const timeoutMs = Number(process.env.UI_SMOKE_TIMEOUT_MS || "120000");

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const consoleLog = [];
  const pageErrors = [];
  const apiLog = [];

  page.on("console", (msg) => {
    consoleLog.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on("pageerror", (err) => {
    pageErrors.push(err.message || String(err));
  });
  page.on("response", (resp) => {
    const url = resp.url();
    if (url.includes("/api/")) {
      apiLog.push(`${resp.status()} ${url}`);
    }
  });

  await page.goto(`${baseUrl}/`, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForSelector("#sendBtn", { timeout: 30000 });
  await page.waitForSelector("#sessions .session-item", { timeout: 30000 });

  // Let the app finish init and render editor.
  await page.waitForTimeout(1200);

  const editorMode = await page.evaluate(() => {
    if (document.querySelector("#editor .cm-content")) return "codemirror";
    if (document.querySelector("#editor textarea.editor-fallback")) return "fallback-textarea";
    return "missing";
  });

  if (editorMode === "codemirror") {
    await page.locator("#editor .cm-content").click();
    await page.keyboard.type(prompt);
  } else if (editorMode === "fallback-textarea") {
    await page.fill("#editor textarea.editor-fallback", prompt);
  } else {
    throw new Error("Editor did not render");
  }

  await page.click("#sendBtn");

  await page.waitForFunction(() => {
    const bodies = Array.from(document.querySelectorAll("#conversation .msg.assistant .msg-body"));
    if (!bodies.length) return false;
    const text = (bodies[bodies.length - 1].innerText || "").trim();
    return text.length > 0 && !text.includes("(error)");
  }, { timeout: timeoutMs });

  const result = await page.evaluate(() => {
    const assistantBodies = Array.from(document.querySelectorAll("#conversation .msg.assistant .msg-body"));
    const userBodies = Array.from(document.querySelectorAll("#conversation .msg.user .msg-body"));
    return {
      sessionCount: document.querySelectorAll("#sessions .session-item").length,
      editorMode: document.querySelector("#editor .cm-content")
        ? "codemirror"
        : (document.querySelector("#editor textarea.editor-fallback") ? "fallback-textarea" : "missing"),
      lastUser: userBodies[userBodies.length - 1]?.innerText?.trim() || "",
      lastAssistant: assistantBodies[assistantBodies.length - 1]?.innerText?.trim() || "",
    };
  });

  console.log(JSON.stringify({
    ok: true,
    baseUrl,
    ...result,
    apiLogTail: apiLog.slice(-10),
    consoleTail: consoleLog.slice(-20),
    pageErrors,
  }, null, 2));

  await browser.close();
}

main().catch((err) => {
  console.error("[ui-smoke] failure:", err && err.stack ? err.stack : err);
  process.exit(1);
});

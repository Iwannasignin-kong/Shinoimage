/**
 * ShinoGraph Background Service Worker
 * Handles context menus, commands, and communication with backend.
 */

const API_BASE = "http://localhost:8000/api";

// Context menu setup
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "shinograph-capture-selection",
    title: "ShinoGraph: 捕获选中内容",
    contexts: ["selection"],
  });
  chrome.contextMenus.create({
    id: "shinograph-capture-page",
    title: "ShinoGraph: 截图当前页面",
    contexts: ["page"],
  });
});

// Context menu click handler
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "shinograph-capture-selection" && info.selectionText) {
    await captureText(info.selectionText, tab.url, tab.title);
  } else if (info.menuItemId === "shinograph-capture-page") {
    await captureScreenshot(tab);
  }
});

// Keyboard shortcut handler
chrome.commands.onCommand.addListener(async (command) => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (command === "capture-screenshot") {
    await captureScreenshot(tab);
  } else if (command === "capture-selection") {
    chrome.tabs.sendMessage(tab.id, { action: "getSelection" }, async (response) => {
      if (response?.text) {
        await captureText(response.text, tab.url, tab.title);
      }
    });
  }
});

// Message handler from content script / popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "captureRegion") {
    handleRegionCapture(msg.imageData, sender.tab).then(sendResponse);
    return true; // async response
  }
  if (msg.action === "chat") {
    handleChat(msg.question).then(sendResponse);
    return true;
  }
});

async function captureScreenshot(tab) {
  const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: "png" });
  const blob = await (await fetch(dataUrl)).blob();
  const formData = new FormData();
  formData.append("image", blob, "screenshot.png");
  formData.append("source_url", tab.url || "");
  formData.append("source_title", tab.title || "");

  const res = await fetch(`${API_BASE}/notes/capture`, { method: "POST", body: formData });
  const result = await res.json();
  // Notify sidebar of new note
  chrome.runtime.sendMessage({ action: "noteAdded", note: result });
}

async function captureText(text, url, title) {
  const formData = new FormData();
  formData.append("text", text);
  formData.append("source_url", url || "");
  formData.append("source_title", title || "");

  const res = await fetch(`${API_BASE}/notes/capture`, { method: "POST", body: formData });
  const result = await res.json();
  chrome.runtime.sendMessage({ action: "noteAdded", note: result });
}

async function handleRegionCapture(imageDataUrl, tab) {
  const blob = await (await fetch(imageDataUrl)).blob();
  const formData = new FormData();
  formData.append("image", blob, "region.png");
  formData.append("source_url", tab?.url || "");
  formData.append("source_title", tab?.title || "");

  const res = await fetch(`${API_BASE}/notes/capture`, { method: "POST", body: formData });
  return res.json();
}

async function handleChat(question) {
  const res = await fetch(`${API_BASE}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

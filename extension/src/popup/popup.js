const API_BASE = "http://localhost:8000/api";

document.getElementById("captureBtn").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, { action: "startRegionCapture" });
  window.close();
});

document.getElementById("captureTextBtn").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, { action: "getSelection" }, async (response) => {
    if (response?.text) {
      const formData = new FormData();
      formData.append("text", response.text);
      formData.append("source_url", tab.url || "");
      formData.append("source_title", tab.title || "");
      await fetch(`${API_BASE}/notes/capture`, { method: "POST", body: formData });
    }
  });
  window.close();
});

document.getElementById("openSidebar").addEventListener("click", () => {
  chrome.sidePanel.open({ windowId: chrome.windows.WINDOW_ID_CURRENT });
  window.close();
});

// Load stats
(async () => {
  try {
    const res = await fetch(`${API_BASE}/notes/?limit=0`);
    const notes = await res.json();
    const graphRes = await fetch(`${API_BASE}/graph/`);
    const graph = await graphRes.json();
    document.getElementById("stats").textContent =
      `${notes.length} 条笔记 · ${graph.nodes?.length || 0} 个概念 · ${graph.edges?.length || 0} 个关联`;
  } catch {
    document.getElementById("stats").textContent = "后端未连接，请启动服务";
  }
})();

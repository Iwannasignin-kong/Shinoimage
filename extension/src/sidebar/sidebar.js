/**
 * ShinoGraph Sidebar — Notes, Graph, Chat
 */

const API_BASE = "http://localhost:8000/api";

// ─── Tab switching ───
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.panel).classList.add("active");

    if (tab.dataset.panel === "graph") loadGraph();
    if (tab.dataset.panel === "notes") loadNotes();
  });
});

// ─── Notes ───
async function loadNotes() {
  try {
    const res = await fetch(`${API_BASE}/notes/`);
    const notes = await res.json();
    const container = document.getElementById("notesList");
    container.innerHTML = notes
      .map(
        (n) => `
      <div class="note-card">
        <div class="title">${n.source_title || "未命名笔记"}</div>
        <div class="summary">${n.summary || ""}</div>
        <div class="time">${n.created_at}</div>
      </div>`
      )
      .join("");
  } catch {
    document.getElementById("notesList").innerHTML =
      '<div class="note-card"><div class="summary">无法连接后端服务</div></div>';
  }
}

// ─── Graph (simple force-directed with SVG) ───
async function loadGraph() {
  try {
    const res = await fetch(`${API_BASE}/graph/`);
    const data = await res.json();
    renderGraph(data);
  } catch {
    console.error("Failed to load graph");
  }
}

function renderGraph(data) {
  const svg = document.getElementById("graphCanvas");
  const width = svg.clientWidth || 400;
  const height = svg.clientHeight || 400;
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = "";

  if (!data.nodes?.length) {
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", width / 2);
    text.setAttribute("y", height / 2);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("fill", "#94a3b8");
    text.setAttribute("font-size", "14");
    text.textContent = "暂无知识图谱数据";
    svg.appendChild(text);
    return;
  }

  // Simple force layout simulation
  const nodes = data.nodes.map((n, i) => ({
    ...n,
    x: width / 2 + Math.cos((i / data.nodes.length) * Math.PI * 2) * 120,
    y: height / 2 + Math.sin((i / data.nodes.length) * Math.PI * 2) * 120,
  }));

  const nodeMap = {};
  nodes.forEach((n) => (nodeMap[n.id] = n));

  // Draw edges
  data.edges.forEach((e) => {
    const src = nodeMap[e.source];
    const tgt = nodeMap[e.target];
    if (!src || !tgt) return;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", src.x);
    line.setAttribute("y1", src.y);
    line.setAttribute("x2", tgt.x);
    line.setAttribute("y2", tgt.y);
    line.setAttribute("stroke", "#334155");
    line.setAttribute("stroke-width", Math.min(e.strength, 4));
    svg.appendChild(line);
  });

  // Draw nodes
  nodes.forEach((n) => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", n.x);
    circle.setAttribute("cy", n.y);
    circle.setAttribute("r", 6 + Math.min(n.count * 2, 20));
    circle.setAttribute("fill", "#6366f1");
    circle.setAttribute("opacity", "0.8");
    g.appendChild(circle);

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", n.x);
    text.setAttribute("y", n.y + 20);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("fill", "#e2e8f0");
    text.setAttribute("font-size", "11");
    text.textContent = n.name;
    g.appendChild(text);

    svg.appendChild(g);
  });
}

// ─── Chat ───
document.getElementById("chatSend").addEventListener("click", sendChat);
document.getElementById("chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});

async function sendChat() {
  const input = document.getElementById("chatInput");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";

  appendMessage(question, "user");

  try {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    appendMessage(data.answer, "ai");
  } catch {
    appendMessage("无法连接后端服务", "ai");
  }
}

function appendMessage(text, role) {
  const container = document.getElementById("chatMessages");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

// ─── Listen for new notes ───
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "noteAdded") {
    loadNotes();
  }
});

// Initial load
loadNotes();

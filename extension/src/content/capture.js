/**
 * Content script for region screenshot capture.
 * Injects a draggable selection overlay when activated.
 */

let isSelecting = false;
let overlay = null;
let startX, startY;

// Listen for selection request from background
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getSelection") {
    sendResponse({ text: window.getSelection().toString() });
  }
  if (msg.action === "startRegionCapture") {
    startRegionCapture();
  }
});

function startRegionCapture() {
  if (isSelecting) return;
  isSelecting = true;

  overlay = document.createElement("div");
  overlay.className = "shinograph-overlay";
  document.body.appendChild(overlay);

  const selection = document.createElement("div");
  selection.className = "shinograph-selection";
  overlay.appendChild(selection);

  overlay.addEventListener("mousedown", (e) => {
    startX = e.clientX;
    startY = e.clientY;
    selection.style.left = `${startX}px`;
    selection.style.top = `${startY}px`;
    selection.style.width = "0";
    selection.style.height = "0";
    selection.style.display = "block";
  });

  overlay.addEventListener("mousemove", (e) => {
    if (!startX) return;
    const w = e.clientX - startX;
    const h = e.clientY - startY;
    selection.style.width = `${Math.abs(w)}px`;
    selection.style.height = `${Math.abs(h)}px`;
    selection.style.left = `${Math.min(startX, e.clientX)}px`;
    selection.style.top = `${Math.min(startY, e.clientY)}px`;
  });

  overlay.addEventListener("mouseup", async (e) => {
    const rect = {
      x: parseInt(selection.style.left),
      y: parseInt(selection.style.top),
      width: parseInt(selection.style.width),
      height: parseInt(selection.style.height),
    };
    cleanup();

    if (rect.width < 10 || rect.height < 10) return;

    // Use canvas to crop the visible area
    // Note: actual implementation needs chrome.tabs.captureVisibleTab from background
    chrome.runtime.sendMessage({
      action: "captureRegion",
      rect,
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") cleanup();
  });
}

function cleanup() {
  if (overlay) {
    overlay.remove();
    overlay = null;
  }
  isSelecting = false;
  startX = startY = null;
}

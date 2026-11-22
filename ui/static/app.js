/**
 * TITAN Desktop Controller v1.3
 * Human-Crafted Linear / Raycast Style Workspace Controller
 */

let isListening = false;
let autoSpeak = true;
let activeModel = "llama3.2:3b";

let currentAgentMode = "orchestrator";

// --- Tab / View Switching ---
function switchView(tabId) {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });
  document.querySelectorAll(".view-panel").forEach(panel => {
    panel.classList.toggle("active", panel.id === tabId);
  });
}

// --- OpenJarvis Agent Mode Selection ---
function selectAgentMode(mode) {
  currentAgentMode = mode;
  document.querySelectorAll(".mode-pill").forEach(pill => {
    pill.classList.toggle("active", pill.dataset.mode === mode);
  });
  if (window.pywebview && window.pywebview.api && window.pywebview.api.set_agent_mode) {
    window.pywebview.api.set_agent_mode(mode);
  }
  const modeNames = {
    orchestrator: "⚡ Orchestrator (Auto Tool Execution)",
    native_react: "🧠 Native ReAct (Thought-Action-Observation)",
    code_interpreter: "💻 Code Assistant (Python Sandbox)",
    deep_research: "🔍 Deep Research (Knowledge Base)",
    morning_digest: "📋 Daily Operative (Briefing & Health)",
    simple: "💬 Simple (Fast Chat)"
  };
  appendMessage("System", `TITAN agent mode switched to: ${modeNames[mode] || mode}`, "assistant");
}

// --- Chat & Message Handling ---
function appendMessage(sender, text, roleClass) {
  const thread = document.getElementById("chatThread");
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${roleClass}`;

  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.innerHTML = `<span class="author">${sender}</span><span class="timestamp">${timeStr}</span>`;

  const body = document.createElement("div");
  body.className = "message-body";
  
  if (roleClass === "assistant") {
    body.innerHTML = formatAssistantContent(text);
  } else {
    body.innerText = text;
  }

  msgDiv.appendChild(meta);
  msgDiv.appendChild(body);
  thread.appendChild(msgDiv);

  // Smooth pinning to bottom
  requestAnimationFrame(() => {
    thread.scrollTop = thread.scrollHeight;
  });
}

function formatAssistantContent(rawText) {
  if (!rawText) return "";

  // 1. Process code blocks ```lang ... ```
  let formatted = rawText.replace(/```([a-zA-Z0-9_]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang || "code";
    const escapedCode = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `
      <div class="code-card">
        <div class="code-header">
          <span class="lang-tag">${language.toUpperCase()}</span>
          <button class="copy-btn" onclick="copyCode(this)">Copy Code</button>
        </div>
        <pre><code>${escapedCode}</code></pre>
      </div>
    `;
  });

  // 2. Detect Action Notifications and render as glowing Action Card
  const isAction = /chrome has been launched|launched ['"]|closed ['"]|volume (increased|decreased|mute)|recycle bin|task #|download complete|maintenance complete/i.test(rawText);
  if (isAction && !formatted.includes("class=\"code-card\"")) {
    return `
      <div class="action-card">
        <div class="action-card-header">
          <span class="action-badge">⚡ WORKSPACE ACTION EXECUTED</span>
          <span class="action-status">✔ Verified</span>
        </div>
        <div class="action-card-body">${formatted.replace(/\n/g, "<br/>")}</div>
      </div>
    `;
  }

  // 3. Format markdown bold, bullets, line breaks
  formatted = formatted
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code style='background:rgba(255,255,255,0.08);padding:2px 5px;border-radius:4px;color:#00e5ff;font-family:var(--font-mono);font-size:12px;'>$1</code>")
    .replace(/\n\n/g, "<br/><br/>")
    .replace(/\n- /g, "<br/>• ");

  return formatted;
}

function copyCode(btn) {
  const code = btn.closest(".code-card").querySelector("code").innerText;
  navigator.clipboard.writeText(code).then(() => {
    const orig = btn.innerText;
    btn.innerText = "Copied!";
    btn.style.background = "#10b981";
    btn.style.color = "#000000";
    setTimeout(() => {
      btn.innerText = orig;
      btn.style.background = "";
      btn.style.color = "";
    }, 2000);
  });
}

function appendThinkingMessage(id) {
  const thread = document.getElementById("chatThread");
  const div = document.createElement("div");
  div.id = id;
  div.className = "message assistant";
  div.innerHTML = `
    <div class="message-meta"><span class="author">TITAN</span><span class="timestamp">Just now</span></div>
    <div class="thinking-card">
      <div class="thinking-spinner"></div>
      <span>TITAN is reasoning & orchestrating local subsystems...</span>
    </div>
  `;
  thread.appendChild(div);
  requestAnimationFrame(() => { thread.scrollTop = thread.scrollHeight; });
}

function removeThinkingMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;

  appendMessage("You", text, "user");
  input.value = "";

  const thinkingId = "thinking-" + Date.now();
  appendThinkingMessage(thinkingId);
  setOrbStatus("TITAN is reasoning...", true);

  try {
    if (window.pywebview && window.pywebview.api) {
      const response = await window.pywebview.api.process_user_message(text);
      removeThinkingMessage(thinkingId);
      appendMessage("TITAN", response, "assistant");
    } else {
      setTimeout(() => {
        removeThinkingMessage(thinkingId);
        appendMessage("TITAN", "Simulation response: " + text, "assistant");
      }, 500);
    }
  } catch (err) {
    removeThinkingMessage(thinkingId);
    appendMessage("TITAN", "Communication error: " + err, "assistant");
  } finally {
    setOrbStatus("TITAN is ready. Type or speak your command.", false);
  }
}

function handleInputKey(e) {
  if (e.key === "Enter") {
    sendMessage();
  }
}

function setOrbStatus(statusText, isBusy = false) {
  const el = document.getElementById("orbStatus");
  const orb = document.getElementById("statusOrb");
  if (el) el.textContent = statusText;
  if (orb) orb.classList.toggle("busy", isBusy);
}

// --- Voice Recognition ---
async function toggleMic() {
  const btn = document.getElementById("micBtn");
  const orb = document.getElementById("voiceOrb");

  if (!isListening) {
    isListening = true;
    if (btn) btn.classList.add("active");
    if (orb) orb.classList.add("listening");
    setOrbStatus("Listening to your voice...", true);

    try {
      if (window.pywebview && window.pywebview.api) {
        const spokenText = await window.pywebview.api.listen_voice();
        if (spokenText) {
          document.getElementById("userInput").value = spokenText;
          sendMessage();
        } else {
          setOrbStatus("No speech detected.", false);
        }
      }
    } catch (e) {
      console.error("Mic error:", e);
    } finally {
      isListening = false;
      if (btn) btn.classList.remove("active");
      if (orb) orb.classList.remove("listening");
      setOrbStatus("TITAN is ready. Type or speak your command.", false);
    }
  }
}

// --- Quick Actions ---
async function quickAction(actionType) {
  setOrbStatus(`Executing ${actionType}...`, true);

  if (!window.pywebview || !window.pywebview.api) {
    appendMessage("System", `Triggered: ${actionType} (Preview Mode)`, "assistant");
    setOrbStatus("TITAN is ready.", false);
    return;
  }

  try {
    const result = await window.pywebview.api.trigger_quick_action(actionType);
    appendMessage("TITAN", result, "assistant");
  } catch (err) {
    appendMessage("TITAN", `Action error: ${err}`, "assistant");
  } finally {
    setOrbStatus("TITAN is ready. Type or speak your command.", false);
  }
}

function selectModel(modelName) {
  activeModel = modelName;
  const label = modelName.includes("hermes") ? "Hermes 3" : (modelName.includes("moondream") ? "Moondream" : "Llama 3.2");
  document.getElementById("activeModelVal").textContent = label;

  document.querySelectorAll(".card").forEach(c => c.classList.remove("active"));
  if (modelName.includes("llama")) {
    document.getElementById("card-llama").classList.add("active");
  } else if (modelName.includes("hermes")) {
    document.getElementById("card-hermes").classList.add("active");
  }

  if (window.pywebview && window.pywebview.api && window.pywebview.api.switch_model) {
    window.pywebview.api.switch_model(modelName);
  }
  appendMessage("System", `Active reasoning model switched to ${label}.`, "assistant");
}

function toggleAutoSpeak() {
  const chk = document.getElementById("autoSpeakCheck").checked;
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.set_auto_speak(chk);
  }
}

function saveSettings() {
  appendMessage("System", "Preferences saved successfully.", "assistant");
}

function minimizeWindow() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.minimize_window) {
    window.pywebview.api.minimize_window();
  }
}

function maximizeWindow() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.maximize_window) {
    window.pywebview.api.maximize_window();
  }
}

function closeWindow() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.close_window) {
    window.pywebview.api.close_window();
  } else {
    window.close();
  }
}

// --- Telemetry Polling Loop ---
async function updateTelemetry() {
  try {
    if (window.pywebview && window.pywebview.api) {
      const stats = await window.pywebview.api.get_telemetry();
      if (stats) {
        // GPU
        const gpu = stats.gpu || {};
        const vramUsed = (gpu.vram_used_mb / 1024).toFixed(1);
        const vramTotal = (gpu.vram_total_mb / 1024).toFixed(1);
        document.getElementById("gpuMemVal").textContent = `${vramUsed} / ${vramTotal} GB`;
        document.getElementById("metric-gpu").textContent = `${gpu.vram_used_mb || 0} MB (${gpu.vram_percent || 0}%)`;
        document.getElementById("m-fill-gpu").style.width = `${gpu.vram_percent || 0}%`;

        // CPU
        const cpu = stats.cpu || {};
        document.getElementById("metric-cpu").textContent = `${cpu.percent || 0}%`;
        document.getElementById("m-fill-cpu").style.width = `${cpu.percent || 0}%`;

        // RAM
        const ram = stats.ram || {};
        document.getElementById("metric-ram").textContent = `${ram.used_gb || 0} / ${ram.total_gb || 16} GB`;
        document.getElementById("m-fill-ram").style.width = `${ram.percent || 0}%`;
      }
    }
  } catch (err) {}
}

setInterval(updateTelemetry, 2500);
window.addEventListener("pywebviewready", () => {
  updateTelemetry();
});

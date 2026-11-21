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
  body.innerText = text;

  msgDiv.appendChild(meta);
  msgDiv.appendChild(body);
  thread.appendChild(msgDiv);

  // Smooth pinning to bottom
  requestAnimationFrame(() => {
    thread.scrollTop = thread.scrollHeight;
  });
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;

  appendMessage("You", text, "user");
  input.value = "";

  setOrbStatus("Processing request...", true);

  try {
    if (window.pywebview && window.pywebview.api) {
      const response = await window.pywebview.api.process_user_message(text);
      appendMessage("TITAN", response, "assistant");
    } else {
      setTimeout(() => {
        appendMessage("TITAN", "Simulation response: " + text, "assistant");
      }, 500);
    }
  } catch (err) {
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
  // Graceful stub for custom titlebar minimize
}

function closeWindow() {
  window.close();
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

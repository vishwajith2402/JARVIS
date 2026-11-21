/**
 * T.I.T.A.N. Desktop Dashboard Frontend Controller v1.2.0
 * Multi-Tab Tactical Interface with Real-Time Audio FX & Arc Reactor Visualizer
 */

let isListening = false;
let autoSpeak = true;
let currentActiveModel = "llama3.2:3b";

// --- Tab Switching Logic ---
function switchTab(tabId) {
  playAudioBeep(600, 0.04);
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.classList.toggle("active", tab.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.toggle("active", pane.id === tabId);
  });
}

// --- Procedural Web Audio API SFX (Iron Man UI Sounds) ---
let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

function playAudioBeep(freq = 800, duration = 0.05, type = "sine") {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);

    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {
    // Audio context may require first user gesture
  }
}

// --- Holographic Arc Reactor Canvas Animation ---
const canvas = document.getElementById("arcCanvas");
const ctx = canvas.getContext("2d");
let angle = 0;

function drawArcReactor() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  // Outer segmented ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle * 0.012);
  ctx.beginPath();
  ctx.arc(0, 0, 85, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.35)";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 8]);
  ctx.stroke();
  ctx.restore();

  // Reverse middle tactical ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-angle * 0.02);
  ctx.beginPath();
  ctx.arc(0, 0, 65, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.7)";
  ctx.lineWidth = 3;
  ctx.setLineDash([16, 12]);
  ctx.stroke();
  ctx.restore();

  // Internal glowing pulse core
  const pulse = Math.sin(angle * 0.08) * 5;
  ctx.beginPath();
  ctx.arc(cx, cy, 32 + pulse, 0, Math.PI * 2);
  const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, 38 + pulse);
  grad.addColorStop(0, "#ffffff");
  grad.addColorStop(0.3, "rgba(0, 240, 255, 0.85)");
  grad.addColorStop(1, "rgba(0, 119, 255, 0.08)");
  ctx.fillStyle = grad;
  ctx.fill();

  // Hologram Crosshairs
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle * 0.006);
  for (let i = 0; i < 4; i++) {
    ctx.rotate(Math.PI / 2);
    ctx.beginPath();
    ctx.moveTo(42, 0);
    ctx.lineTo(58, 0);
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 1.8;
    ctx.stroke();
  }
  ctx.restore();

  angle += 1;
  requestAnimationFrame(drawArcReactor);
}

// Start visualizer loop
drawArcReactor();

// --- Message & Chat Functions ---
function appendMessage(sender, text, roleClass) {
  playAudioBeep(roleClass === "user" ? 700 : 950, 0.04);
  const chatBox = document.getElementById("chatBox");
  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg ${roleClass}`;

  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const tag = document.createElement("div");
  tag.className = "speaker-tag";
  tag.innerHTML = `<span>${sender}</span><span class="time-stamp">${timeStr}</span>`;

  const content = document.createElement("div");
  content.className = "msg-content";
  content.innerText = text;

  msgDiv.appendChild(tag);
  msgDiv.appendChild(content);
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;

  appendMessage("YOU", text, "user");
  input.value = "";

  setArcStatus("PROCESSING INSTRUCTION, SIR...");

  try {
    if (window.pywebview && window.pywebview.api) {
      const response = await window.pywebview.api.process_user_message(text);
      appendMessage("T.I.T.A.N.", response, "jarvis");
    } else {
      setTimeout(() => {
        appendMessage("T.I.T.A.N.", "System preview mode response: " + text, "jarvis");
      }, 500);
    }
  } catch (err) {
    appendMessage("T.I.T.A.N.", "Subsystem communication error: " + err, "jarvis");
  } finally {
    setArcStatus("AWAITING INSTRUCTION, SIR");
  }
}

function handleKey(e) {
  if (e.key === "Enter") {
    sendMessage();
  }
}

function setArcStatus(text) {
  const el = document.getElementById("arcText");
  if (el) el.textContent = text;
}

// --- Voice Push-To-Talk ---
async function toggleMic() {
  const btn = document.getElementById("micBtn");
  if (!isListening) {
    isListening = true;
    btn.classList.add("active");
    playAudioBeep(1200, 0.08);
    setArcStatus("LISTENING TO YOUR VOICE, SIR...");
    try {
      if (window.pywebview && window.pywebview.api) {
        const spokenText = await window.pywebview.api.listen_voice();
        if (spokenText) {
          document.getElementById("userInput").value = spokenText;
          sendMessage();
        } else {
          setArcStatus("NO SPEECH DETECTED, SIR");
        }
      }
    } catch (e) {
      console.error("Mic error:", e);
    } finally {
      isListening = false;
      btn.classList.remove("active");
      setArcStatus("AWAITING INSTRUCTION, SIR");
    }
  }
}

// --- Quick Actions & Tools ---
async function quickAction(actionType) {
  playAudioBeep(850, 0.04);
  setArcStatus(`EXECUTING: ${actionType.toUpperCase()}`);

  if (!window.pywebview || !window.pywebview.api) {
    appendMessage("SYSTEM", `Triggered action: ${actionType} (Preview mode)`, "jarvis");
    setArcStatus("AWAITING INSTRUCTION, SIR");
    return;
  }

  try {
    const result = await window.pywebview.api.trigger_quick_action(actionType);
    appendMessage("T.I.T.A.N.", result, "jarvis");
  } catch (err) {
    appendMessage("T.I.T.A.N.", `Action error: ${err}`, "jarvis");
  } finally {
    setArcStatus("AWAITING INSTRUCTION, SIR");
  }
}

function toggleVoiceFeedback() {
  const checked = document.getElementById("voiceToggle").checked;
  playAudioBeep(checked ? 900 : 500, 0.05);
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.set_auto_speak(checked);
  }
}

async function testVoice() {
  playAudioBeep(1000, 0.06);
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.test_voice_synthesis();
  }
}

// --- Vision Analysis Workspace ---
async function runVisionAnalysis() {
  playAudioBeep(1100, 0.05);
  const outEl = document.getElementById("visionOutputText");
  outEl.textContent = "Initiating optical screen capture and dispatching to Moondream vision core...";

  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.trigger_quick_action("screen_capture");
      outEl.textContent = res;
    } catch (err) {
      outEl.textContent = "Vision analysis failed: " + err;
    }
  } else {
    setTimeout(() => {
      outEl.textContent = "Vision analysis preview: Screen captured. Desktop active with J.A.R.V.I.S. HUD and code editor windows open.";
    }, 1200);
  }
}

// --- Model Hot-Swapping ---
function selectModel(modelName) {
  playAudioBeep(900, 0.05);
  currentActiveModel = modelName;
  document.getElementById("active-model-badge").textContent = modelName.toUpperCase();

  document.querySelectorAll(".model-card").forEach(c => c.classList.remove("active"));
  if (modelName.includes("llama")) {
    document.getElementById("card-llama").classList.add("active");
  } else if (modelName.includes("hermes")) {
    document.getElementById("card-hermes").classList.add("active");
  }

  if (window.pywebview && window.pywebview.api && window.pywebview.api.switch_model) {
    window.pywebview.api.switch_model(modelName);
  }
  appendMessage("SYSTEM", `Active AI reasoning model hot-swapped to '${modelName}', Sir.`, "jarvis");
}

function saveSettings() {
  playAudioBeep(950, 0.05);
  appendMessage("SYSTEM", "User preferences and honorific updated successfully, Sir.", "jarvis");
}

// --- Realtime Telemetry Poller ---
async function updateTelemetry() {
  try {
    if (window.pywebview && window.pywebview.api) {
      const stats = await window.pywebview.api.get_telemetry();
      if (stats) {
        // GPU
        const gpu = stats.gpu || {};
        document.getElementById("gpu-vram-text").textContent = `${gpu.vram_used_mb || 0} / ${gpu.vram_total_mb || 4096} MB`;
        document.getElementById("gpu-vram-bar").style.width = `${gpu.vram_percent || 0}%`;
        document.getElementById("gpu-temp").textContent = `${gpu.temperature_c || 0}°C`;
        document.getElementById("gpu-util").textContent = `${gpu.gpu_util_percent || 0}%`;

        // CPU
        const cpu = stats.cpu || {};
        document.getElementById("cpu-percent-text").textContent = `${cpu.percent || 0}%`;
        document.getElementById("cpu-bar").style.width = `${cpu.percent || 0}%`;
        if (cpu.frequency_mhz) {
          document.getElementById("cpu-freq").textContent = `${cpu.frequency_mhz} MHz`;
        }

        // RAM
        const ram = stats.ram || {};
        document.getElementById("ram-text").textContent = `${ram.used_gb || 0} / ${ram.total_gb || 16} GB`;
        document.getElementById("ram-bar").style.width = `${ram.percent || 0}%`;

        // Battery
        const bat = stats.battery || {};
        const pwr = bat.power_plugged ? "AC" : "BAT";
        document.getElementById("battery-text").textContent = `${bat.percent || 100}% [${pwr}]`;
        document.getElementById("battery-bar").style.width = `${bat.percent || 100}%`;
      }
    }
  } catch (err) {
    // waiting for bridge ready
  }
}

// Polling intervals
setInterval(updateTelemetry, 2000);
window.addEventListener("pywebviewready", () => {
  updateTelemetry();
});

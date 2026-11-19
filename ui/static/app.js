/**
 * J.A.R.V.I.S. Desktop Dashboard Frontend Controller
 * Communicates with Python backend via window.pywebview.api
 */

let isListening = false;
let autoSpeak = true;

// --- Arc Reactor Holographic Canvas ---
const canvas = document.getElementById("arcCanvas");
const ctx = canvas.getContext("2d");
let angle = 0;

function drawArcReactor() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  // Outer Glowing Ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle * 0.015);
  ctx.beginPath();
  ctx.arc(0, 0, 75, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.4)";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 6]);
  ctx.stroke();
  ctx.restore();

  // Reverse Inner Segment Ring
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-angle * 0.025);
  ctx.beginPath();
  ctx.arc(0, 0, 55, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.7)";
  ctx.lineWidth = 3;
  ctx.setLineDash([16, 12]);
  ctx.stroke();
  ctx.restore();

  // Core Pulse
  const pulse = Math.sin(angle * 0.08) * 4;
  ctx.beginPath();
  ctx.arc(cx, cy, 28 + pulse, 0, Math.PI * 2);
  const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, 32 + pulse);
  grad.addColorStop(0, "#ffffff");
  grad.addColorStop(0.3, "rgba(0, 240, 255, 0.8)");
  grad.addColorStop(1, "rgba(0, 119, 255, 0.1)");
  ctx.fillStyle = grad;
  ctx.fill();

  // Arc Crosshairs
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle * 0.005);
  for (let i = 0; i < 4; i++) {
    ctx.rotate(Math.PI / 2);
    ctx.beginPath();
    ctx.moveTo(35, 0);
    ctx.lineTo(48, 0);
    ctx.strokeStyle = "#00f0ff";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }
  ctx.restore();

  angle += 1;
  requestAnimationFrame(drawArcReactor);
}

// Start visualizer
drawArcReactor();

// --- Message & Chat Functions ---
function appendMessage(sender, text, roleClass) {
  const chatBox = document.getElementById("chatBox");
  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-msg ${roleClass}`;
  
  const tag = document.createElement("div");
  tag.className = "speaker-tag";
  tag.textContent = sender;

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
      appendMessage("J.A.R.V.I.S.", response, "jarvis");
    } else {
      setTimeout(() => {
        appendMessage("J.A.R.V.I.S.", "System offline simulation: " + text, "jarvis");
      }, 500);
    }
  } catch (err) {
    appendMessage("J.A.R.V.I.S.", "Subsystem communication error: " + err, "jarvis");
  } finally {
    setArcStatus("AWAITING INPUT, SIR");
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
      setArcStatus("AWAITING INPUT, SIR");
    }
  }
}

// --- Quick Actions ---
async function quickAction(actionType) {
  if (!window.pywebview || !window.pywebview.api) {
    appendMessage("SYSTEM", `Triggered action: ${actionType} (Preview mode)`, "jarvis");
    return;
  }
  setArcStatus(`EXECUTING: ${actionType.toUpperCase()}`);
  const result = await window.pywebview.api.trigger_quick_action(actionType);
  appendMessage("J.A.R.V.I.S.", result, "jarvis");
  setArcStatus("AWAITING INPUT, SIR");
}

function toggleVoiceFeedback() {
  const checked = document.getElementById("voiceToggle").checked;
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.set_auto_speak(checked);
  }
}

async function testVoice() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.test_voice_synthesis();
  }
}

// --- Realtime Hardware Telemetry Loop ---
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
    // silently wait for backend connection
  }
}

// Poll telemetry every 2 seconds
setInterval(updateTelemetry, 2000);
window.addEventListener("pywebviewready", () => {
  updateTelemetry();
});

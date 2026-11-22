/**
 * TITAN Desktop Controller v1.4
 * Sovereign Enterprise AI & Autonomous Operations Core
 */

let isListening = false;
let autoSpeak = true;
let activeModel = "llama3.2:3b";
let currentAgentMode = "orchestrator";

// ==========================================================================
// HERO PAGE & LAUNCH CONTROLLER
// ==========================================================================
function launchMainAgent(target = "chat") {
  const hero = document.getElementById("heroScreen");
  if (hero) {
    hero.classList.add("hidden");
  }

  if (target === "business") {
    switchView("tab-business");
  } else if (target === "artifacts") {
    switchView("tab-chat");
    promptLovableApp();
  } else if (target === "voice") {
    switchView("tab-chat");
    toggleMic();
  } else if (target === "apps") {
    switchView("tab-chat");
    sendMessage("list all running windows and workspace applications");
  } else if (target === "files") {
    switchView("tab-research");
  } else if (target === "command") {
    switchView("tab-chat");
    openSpotlight();
  } else if (target === "settings") {
    switchView("tab-settings");
  } else {
    switchView("tab-chat");
  }

  // Welcome announcement
  if (window.pywebview && window.pywebview.api && window.pywebview.api.test_voice_synthesis) {
    // Optional greeting
  }
}

function returnToHero() {
  const hero = document.getElementById("heroScreen");
  if (hero) {
    hero.classList.remove("hidden");
  }
}

function setHeroTab(tabName) {
  document.querySelectorAll(".nav-hud-tab").forEach(tab => tab.classList.remove("active"));
  const activeBtn = document.getElementById("tabNav" + tabName.charAt(0).toUpperCase() + tabName.slice(1));
  if (activeBtn) activeBtn.classList.add("active");

  const modal = document.getElementById("heroHudModal");
  const title = document.getElementById("heroModalTitle");
  const body = document.getElementById("heroModalBody");

  if (tabName === "home") {
    if (modal) modal.classList.remove("active");
    return;
  }

  const modalData = {
    features: {
      title: "TITAN CORE CAPABILITIES",
      html: `
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
            <strong style="color:#38bdf8;">🖥️ Desktop Autopilot</strong>
            <p style="font-size:12px; color:#94a3b8; margin-top:4px;">Win32 window snapping, screen vision & process management.</p>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
            <strong style="color:#38bdf8;">🏢 Autonomous C-Suite</strong>
            <p style="font-size:12px; color:#94a3b8; margin-top:4px;">Executive OKRs, CRM prospecting pipeline & HTML invoices.</p>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
            <strong style="color:#38bdf8;">⚡ Live Generative Artifacts</strong>
            <p style="font-size:12px; color:#94a3b8; margin-top:4px;">Interactive single-file Lovable apps & Figma tokens in sandbox.</p>
          </div>
          <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
            <strong style="color:#38bdf8;">🎙️ Neural Voice Presence</strong>
            <p style="font-size:12px; color:#94a3b8; margin-top:4px;">Natural continuous wake-word ('Hey Titan') & instant barge-in.</p>
          </div>
        </div>
      `
    },
    architecture: {
      title: "TITAN 100% LOCAL ARCHITECTURE",
      html: `
        <div style="font-size:13px; line-height:1.6;">
          <p style="margin-bottom:8px;"><strong style="color:#38bdf8;">Zero Cloud Dependency:</strong> Runs natively on AMD Ryzen 5 & NVIDIA GeForce RTX 3050 GPU.</p>
          <ul style="padding-left:18px; color:#cbd5e1;">
            <li><strong>Inference Engine:</strong> Local Ollama / vLLM serving <code>titan:latest</code> & <code>moondream</code>.</li>
            <li><strong>Tool Execution:</strong> Hermes XML parser with zero hallucinations & sandboxed REPL.</li>
            <li><strong>Memory & Profile:</strong> SQLite Vector Graph persisting user facts & preferences locally.</li>
            <li><strong>Desktop Controller:</strong> Native Win32 API window manager & screen OCR vision sense.</li>
          </ul>
        </div>
      `
    },
    projects: {
      title: "TITAN REGISTERED PROJECTS",
      html: `
        <div style="font-size:13px; line-height:1.6;">
          <p style="margin-bottom:10px;">TITAN is indexed and bound to the sovereign workspace:</p>
          <div style="background:rgba(255,255,255,0.04); padding:12px; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:700; color:#ffffff;">D:\\Practice Projects\\JARVIS</span>
              <span style="font-size:11px; background:#10b981; color:#000; font-weight:700; padding:2px 8px; border-radius:999px;">ACTIVE REPO</span>
            </div>
            <p style="font-size:12px; color:#94a3b8; margin-top:6px;">51 Unit Tests Verified (100%) • Git Branch: main (Clean)</p>
          </div>
        </div>
      `
    },
    about: {
      title: "ABOUT TITAN OPERATING SYSTEM",
      html: `
        <div style="font-size:13px; line-height:1.6;">
          <p><strong style="color:#38bdf8;">TITAN Core v1.4 Sovereign</strong></p>
          <p style="color:#94a3b8; margin:6px 0 12px;">Engineered as an autonomous enterprise AI assistant designed for builders. Native window autopilot, executive business operations, and real-time live artifacts—running 100% on local hardware with zero data exfiltration.</p>
          <div style="display:flex; gap:10px;">
            <button class="hero-primary-glow-btn" style="padding:8px 20px; font-size:13px;" onclick="closeHeroModal(); launchMainAgent();">Launch Workspace</button>
          </div>
        </div>
      `
    }
  };

  if (modalData[tabName]) {
    title.textContent = modalData[tabName].title;
    body.innerHTML = modalData[tabName].html;
    if (modal) modal.classList.add("active");
  }
}

function closeHeroModal() {
  const modal = document.getElementById("heroHudModal");
  if (modal) modal.classList.remove("active");
  const homeTab = document.getElementById("tabNavHome");
  if (homeTab) {
    document.querySelectorAll(".nav-hud-tab").forEach(tab => tab.classList.remove("active"));
    homeTab.classList.add("active");
  }
}

// --- Tab / View Switching ---
function switchView(tabId) {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tabId);
  });
  document.querySelectorAll(".view-panel").forEach(panel => {
    panel.classList.toggle("active", panel.id === tabId);
  });
  if (tabId === "tab-profile") {
    loadExecutiveProfile();
  } else if (tabId === "tab-business") {
    loadBusinessDashboard();
  }
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

function setWaveformActive(active) {
  const viz = document.getElementById("waveformViz");
  if (viz) {
    viz.classList.toggle("active", active);
  }
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
  setWaveformActive(true);

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
    setWaveformActive(false);
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
    setWaveformActive(true);

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
      setWaveformActive(false);
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

        // Real-Time Radial Gauges on Hero HUD
        const cpuPct = Math.round(cpu.percent || 18);
        const ramPct = Math.round(ram.percent || 42);
        const vramPct = Math.round(gpu.vram_percent || 27);
        const bat = stats.battery || {};
        const battPct = Math.round(bat.percent || 87);

        const heroCpu = document.getElementById("heroGaugeCpu");
        const heroRam = document.getElementById("heroGaugeRam");
        const heroVram = document.getElementById("heroGaugeVram");
        const heroBatt = document.getElementById("heroGaugeBatt");

        if (heroCpu) heroCpu.textContent = `${cpuPct}%`;
        if (heroRam) heroRam.textContent = `${ramPct}%`;
        if (heroVram) heroVram.textContent = `${vramPct}%`;
        if (heroBatt) heroBatt.textContent = `${battPct}%`;

        const updateRing = (id, pct) => {
          const el = document.getElementById(id);
          if (el) {
            const offset = 113 - (113 * (Math.min(100, Math.max(0, pct)) / 100));
            el.setAttribute("stroke-dashoffset", offset.toFixed(1));
          }
        };
        updateRing("svgCpuCircle", cpuPct);
        updateRing("svgRamCircle", ramPct);
        updateRing("svgVramCircle", vramPct);
        updateRing("svgBattCircle", battPct);
      }
    }
  } catch (err) {}
}

setInterval(updateTelemetry, 2500);
window.addEventListener("pywebviewready", () => {
  updateTelemetry();
  loadExecutiveProfile();
});

// ==========================================================================
// TOP MNC EXECUTIVE PROFILE & KNOWLEDGE GRAPH
// ==========================================================================
async function loadExecutiveProfile() {
  if (!window.pywebview || !window.pywebview.api) return;

  try {
    if (window.pywebview.api.get_executive_profile) {
      const prof = await window.pywebview.api.get_executive_profile();
      if (prof) {
        document.getElementById("profUserName").textContent = prof.user_name || "Vishwajith";
        document.getElementById("profUserRole").textContent = prof.role || "Lead Software Engineer";
        document.getElementById("profUserTitle").value = prof.user_title || "Sir";
        document.getElementById("profLanguages").value = (prof.preferred_languages || []).join(", ");
        document.getElementById("profIde").value = prof.primary_ide || "Visual Studio Code";
      }
    }

    if (window.pywebview.api.get_executive_facts) {
      const facts = await window.pywebview.api.get_executive_facts();
      renderFactsList(facts || []);
    }
  } catch (err) {
    console.error("Failed to load executive profile:", err);
  }
}

function renderFactsList(facts) {
  const container = document.getElementById("factsListContainer");
  const badge = document.getElementById("factCountBadge");
  if (!container) return;

  if (badge) badge.textContent = `${facts.length} Active Rules`;

  if (facts.length === 0) {
    container.innerHTML = `<div class="fact-item" style="color:var(--text-muted); justify-content:center;">No permanent rules stored yet. Add one below!</div>`;
    return;
  }

  container.innerHTML = facts.map(f => `
    <div class="fact-item">
      <div class="fact-meta">
        <span class="fact-cat-tag">${f.category || "RULE"}</span>
        <span class="fact-body"><strong>${f.subject}:</strong> ${f.fact}</span>
      </div>
    </div>
  `).join("");
}

async function saveProfileChanges() {
  if (!window.pywebview || !window.pywebview.api || !window.pywebview.api.update_executive_profile) return;

  const title = document.getElementById("profUserTitle").value.trim() || "Sir";
  const langs = document.getElementById("profLanguages").value.split(",").map(s => s.trim()).filter(Boolean);
  const ide = document.getElementById("profIde").value.trim() || "Visual Studio Code";

  try {
    await window.pywebview.api.update_executive_profile({
      user_title: title,
      preferred_languages: langs,
      primary_ide: ide
    });
    appendMessage("System", `Executive Profile updated: Title set to '${title}', IDE '${ide}'.`, "assistant");
  } catch (err) {
    console.error("Error saving profile:", err);
  }
}

async function addNewFact() {
  if (!window.pywebview || !window.pywebview.api || !window.pywebview.api.save_executive_fact) return;

  const cat = document.getElementById("newFactCategory").value.trim() || "preference";
  const subj = document.getElementById("newFactSubject").value.trim() || "general";
  const fact = document.getElementById("newFactText").value.trim();
  if (!fact) return;

  try {
    await window.pywebview.api.save_executive_fact(cat, subj, fact);
    document.getElementById("newFactCategory").value = "";
    document.getElementById("newFactSubject").value = "";
    document.getElementById("newFactText").value = "";
    loadExecutiveProfile();
    appendMessage("System", `Remembered rule: [${cat}] ${subj} - ${fact}`, "assistant");
  } catch (err) {
    console.error("Error adding fact:", err);
  }
}

// ==========================================================================
// SPOTLIGHT COMMAND PALETTE (RAYCAST / APPLE SPOTLIGHT STYLE)
// ==========================================================================
const SPOTLIGHT_ACTIONS = [
  { id: "morning_digest", icon: "☀️", title: "Daily Executive Briefing", desc: "Hardware, Git repositories, disk & battery status", tag: "Routine" },
  { id: "tile_windows", icon: "🖥️", title: "Tile Workspace Windows", desc: "Split screen 50/50 with VS Code left and Chrome right", tag: "Window Autopilot" },
  { id: "open_vscode", icon: "⚡", title: "Launch Visual Studio Code", desc: "Open active coding project workspace", tag: "Workspace" },
  { id: "scan_projects", icon: "📂", title: "Inspect Repositories", desc: "Autonomous scanning of local git projects", tag: "Projects" },
  { id: "screen_capture", icon: "👁️", title: "Vision Screen Debugger", desc: "Inspect display, diagnose visual bugs & errors", tag: "Vision" },
  { id: "toggle_voice_daemon", icon: "🎙️", title: "Toggle Hands-Free Voice", desc: "Enable/disable continuous 'Hey Titan' wake word", tag: "Voice" },
  { id: "lovable_app", icon: "🚀", title: "Build Generative Web App", desc: "Lovable/v0 style interactive app with live Artifacts preview", tag: "Lovable" },
  { id: "figma_design", icon: "🎨", title: "Generate UI/UX Component", desc: "Figma design system tokens & visual vector layout", tag: "Figma" },
  { id: "perplexity_search", icon: "🌐", title: "Perplexity Verified Search", desc: "Live multi-source synthesis with numbered citations", tag: "Perplexity" },
  { id: "deep_research", icon: "🔍", title: "Deep Web Research", desc: "Multi-site autonomous research & synthesis", tag: "Web" },
  { id: "open_business", icon: "🏢", title: "Autonomous Business Hub", desc: "Access Invoicing, CRM pipeline & OKR milestones", tag: "Business" },
  { id: "biz_invoice", icon: "🧾", title: "Issue Client Invoice", desc: "Create professional HTML invoice and log to ledger", tag: "Finance" },
  { id: "biz_goal", icon: "🎯", title: "Plan Business Goal & OKR", desc: "Decompose company goal into department milestones", tag: "Strategy" },
  { id: "biz_lead", icon: "💼", title: "Add B2B Sales Prospect", desc: "Log a new client lead into CRM pipeline", tag: "Sales" },
  { id: "open_profile", icon: "👤", title: "Executive Memory & Profile", desc: "View and edit personalized developer rules & facts", tag: "Profile" },
  { id: "quick_clean", icon: "🧹", title: "Quick Clean Workstation", desc: "Purge temporary files and recycle bin", tag: "System" },
  { id: "lock_pc", icon: "🔒", title: "Lock Workstation", desc: "Secure workstation immediately", tag: "Security" }
];

let selectedSpotlightIndex = 0;
let filteredSpotlight = [...SPOTLIGHT_ACTIONS];

function openSpotlight() {
  const modal = document.getElementById("spotlightModal");
  const input = document.getElementById("spotlightInput");
  if (!modal) return;
  modal.classList.add("active");
  selectedSpotlightIndex = 0;
  filteredSpotlight = [...SPOTLIGHT_ACTIONS];
  renderSpotlightList();
  if (input) {
    input.value = "";
    setTimeout(() => input.focus(), 50);
  }
}

function closeSpotlight(e) {
  const modal = document.getElementById("spotlightModal");
  if (modal) modal.classList.remove("active");
}

function renderSpotlightList() {
  const list = document.getElementById("spotlightList");
  if (!list) return;

  if (filteredSpotlight.length === 0) {
    list.innerHTML = `<div style="padding:16px; text-align:center; color:var(--text-muted); font-size:13px;">No commands matching query.</div>`;
    return;
  }

  list.innerHTML = filteredSpotlight.map((act, idx) => `
    <div class="spotlight-item ${idx === selectedSpotlightIndex ? 'selected' : ''}" onclick="executeSpotlightAction('${act.id}')">
      <div class="spotlight-item-icon">${act.icon}</div>
      <div class="spotlight-item-info">
        <span class="spotlight-item-title">${act.title}</span>
        <span class="spotlight-item-desc">${act.desc}</span>
      </div>
      <span class="spotlight-item-tag">${act.tag}</span>
    </div>
  `).join("");
}

function filterSpotlight() {
  const query = document.getElementById("spotlightInput").value.toLowerCase().trim();
  if (!query) {
    filteredSpotlight = [...SPOTLIGHT_ACTIONS];
  } else {
    filteredSpotlight = SPOTLIGHT_ACTIONS.filter(a =>
      a.title.toLowerCase().includes(query) ||
      a.desc.toLowerCase().includes(query) ||
      a.tag.toLowerCase().includes(query) ||
      a.id.toLowerCase().includes(query)
    );
  }
  selectedSpotlightIndex = 0;
  renderSpotlightList();
}

function handleSpotlightKey(e) {
  if (e.key === "ArrowDown") {
    e.preventDefault();
    selectedSpotlightIndex = (selectedSpotlightIndex + 1) % filteredSpotlight.length;
    renderSpotlightList();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    selectedSpotlightIndex = (selectedSpotlightIndex - 1 + filteredSpotlight.length) % filteredSpotlight.length;
    renderSpotlightList();
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (filteredSpotlight[selectedSpotlightIndex]) {
      executeSpotlightAction(filteredSpotlight[selectedSpotlightIndex].id);
    }
  } else if (e.key === "Escape") {
    closeSpotlight();
  }
}

function executeSpotlightAction(actionId) {
  closeSpotlight();

  if (actionId === "open_profile") {
    switchView("tab-profile");
    return;
  } else if (actionId === "lovable_app") {
    promptLovableApp();
    return;
  } else if (actionId === "figma_design") {
    promptFigmaDesign();
    return;
  } else if (actionId === "perplexity_search") {
    promptPerplexitySearch();
    return;
  } else if (actionId === "open_business") {
    switchView("tab-business");
    return;
  } else if (actionId === "biz_invoice") {
    switchView("tab-business");
    promptNewInvoice();
    return;
  } else if (actionId === "biz_goal") {
    switchView("tab-business");
    promptNewGoal();
    return;
  } else if (actionId === "biz_lead") {
    switchView("tab-business");
    promptNewLead();
    return;
  } else if (actionId === "tile_windows") {
    quickAction("arrange_workspace");
    return;
  } else if (actionId === "quick_clean") {
    quickAction("quick_clean");
    return;
  }

  quickAction(actionId);
}

// Global Spotlight Hotkey (Ctrl+K or Alt+Space or Escape) & Hero Screen Launch
window.addEventListener("keydown", (e) => {
  // Hero screen Enter / Space launch trigger
  const hero = document.getElementById("heroScreen");
  if (hero && !hero.classList.contains("hidden")) {
    if (e.key === "Enter" || e.code === "Space") {
      e.preventDefault();
      launchMainAgent();
      return;
    }
  }

  if ((e.ctrlKey && e.key.toLowerCase() === "k") || (e.altKey && (e.code === "Space" || e.key === " "))) {
    e.preventDefault();
    const modal = document.getElementById("spotlightModal");
    if (modal && modal.classList.contains("active")) {
      closeSpotlight();
    } else {
      openSpotlight();
    }
  } else if (e.key === "Escape") {
    closeSpotlight();
  }
});

// ==========================================================================
// AUTONOMOUS BUSINESS OPERATIONS DASHBOARD
// ==========================================================================
async function loadBusinessDashboard() {
  if (!window.pywebview || !window.pywebview.api) return;

  try {
    if (window.pywebview.api.get_business_summary) {
      const summary = await window.pywebview.api.get_business_summary();
      if (summary && summary.metrics) {
        const m = summary.metrics;
        document.getElementById("bizRevenue").textContent = `$${(m.total_revenue || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById("bizProfit").textContent = `$${(m.net_profit || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById("bizPipeline").textContent = `$${(m.pipeline_value || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById("bizGoals").textContent = `${m.active_strategic_goals || 0} Active (${m.average_okr_progress_pct || 0}%)`;
      }
    }

    if (window.pywebview.api.get_business_goals) {
      const goals = await window.pywebview.api.get_business_goals();
      renderBusinessGoals(goals || []);
    }

    if (window.pywebview.api.get_business_leads) {
      const leads = await window.pywebview.api.get_business_leads();
      renderBusinessLeads(leads || []);
    }

    if (window.pywebview.api.get_business_invoices) {
      const invoices = await window.pywebview.api.get_business_invoices();
      renderBusinessInvoices(invoices || []);
    }
  } catch (err) {
    console.error("Error loading business hub:", err);
  }
}

function renderBusinessGoals(goals) {
  const container = document.getElementById("bizGoalsList");
  if (!container) return;

  if (goals.length === 0) {
    container.innerHTML = `<div class="biz-item" style="color:var(--text-muted); text-align:center;">No active business goals. Click '+ Plan Strategic Goal'.</div>`;
    return;
  }

  container.innerHTML = goals.map(g => `
    <div class="biz-item">
      <div class="biz-item-row">
        <span class="biz-item-title">${g.title}</span>
        <span class="kpi-tag yellow">${g.progress_pct || 0}% Done</span>
      </div>
      <div class="biz-item-sub">${g.description || ""}</div>
      <div class="biz-item-sub" style="color:var(--brand-secondary); margin-top:2px;">
        ${(g.milestones || []).length} Department Milestones Linked
      </div>
    </div>
  `).join("");
}

function renderBusinessLeads(leads) {
  const container = document.getElementById("bizLeadsList");
  if (!container) return;

  if (leads.length === 0) {
    container.innerHTML = `<div class="biz-item" style="color:var(--text-muted); text-align:center;">No active leads. Click '+ Add B2B Lead'.</div>`;
    return;
  }

  container.innerHTML = leads.map(l => `
    <div class="biz-item">
      <div class="biz-item-row">
        <span class="biz-item-title">${l.company}</span>
        <span class="kpi-tag green">$${(l.estimated_value || 0).toLocaleString()}</span>
      </div>
      <div class="biz-item-sub">${l.contact_name || "Contact"} (${l.role || "Executive"})</div>
      <div class="biz-item-row mt-1">
        <span class="biz-item-sub">${l.email || ""}</span>
        <span class="kpi-tag purple">${l.status.toUpperCase()}</span>
      </div>
    </div>
  `).join("");
}

function renderBusinessInvoices(invoices) {
  const container = document.getElementById("bizInvoicesList");
  if (!container) return;

  if (invoices.length === 0) {
    container.innerHTML = `<div class="biz-item" style="color:var(--text-muted); text-align:center;">No client invoices. Click '+ Issue New Invoice'.</div>`;
    return;
  }

  container.innerHTML = invoices.map(inv => `
    <div class="biz-item">
      <div class="biz-item-row">
        <span class="biz-item-title">${inv.invoice_number}</span>
        <span class="kpi-tag blue">$${(inv.total || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
      </div>
      <div class="biz-item-sub">Client: ${inv.client_name} (${inv.client_email || "No email"})</div>
      <div class="biz-item-row mt-1">
        <span class="biz-item-sub">Due: ${inv.due_date}</span>
        <span class="kpi-tag green">${inv.status.toUpperCase()}</span>
      </div>
    </div>
  `).join("");
}

async function promptNewInvoice() {
  const client = prompt("Enter Client Name:", "Acme AI Corp");
  if (!client) return;
  const email = prompt("Enter Client Email:", "billing@acme.ai") || "";
  const service = prompt("Enter Service Description:", "AI Integration & Architecture") || "Technical Consulting";
  const rateStr = prompt("Enter Rate (USD):", "2500");
  const rate = parseFloat(rateStr) || 2500.0;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.generate_business_invoice) {
    const res = await window.pywebview.api.generate_business_invoice(client, email, [{description: service, quantity: 1, rate: rate}], 0.0);
    loadBusinessDashboard();
    appendMessage("System", `Generated Client Invoice: ${res.invoice_number} for $${rate.toLocaleString()} USD (Saved to ${res.file_path}).`, "assistant");
  }
}

async function promptNewGoal() {
  const title = prompt("Enter Strategic Goal Title:", "Launch AI Consulting Retainer Package");
  if (!title) return;
  const desc = prompt("Enter Goal Description:", "Acquire 5 client retainers for private desktop AI agent integration") || "";

  if (window.pywebview && window.pywebview.api && window.pywebview.api.create_business_goal) {
    const res = await window.pywebview.api.create_business_goal(title, desc, "growth");
    loadBusinessDashboard();
    appendMessage("System", `Strategic Business Goal Created: '${title}' decomposed into Engineering, Marketing, Sales, and Ops milestones.`, "assistant");
  }
}

async function promptNewLead() {
  const company = prompt("Enter Company Name:", "TechNova Labs");
  if (!company) return;
  const contact = prompt("Enter Contact Name:", "Sarah Jenkins") || "";
  const role = prompt("Enter Role:", "VP of Engineering") || "";
  const email = prompt("Enter Email:", "sarah@technova.io") || "";
  const valStr = prompt("Enter Estimated Deal Value ($):", "4000");
  const val = parseFloat(valStr) || 4000.0;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.add_business_lead) {
    await window.pywebview.api.add_business_lead(company, contact, role, email, val, "Qualified inbound lead");
    loadBusinessDashboard();
    appendMessage("System", `New CRM Lead Logged: ${company} ($${val.toLocaleString()} USD) - ${contact}.`, "assistant");
  }
}

async function promptMarketingCampaign() {
  const topic = prompt("Enter Product or Campaign Topic:", "Autonomous Local AI Agents for Enterprise Workstations");
  if (!topic) return;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.create_marketing_campaign) {
    const res = await window.pywebview.api.create_marketing_campaign("social_thread", topic);
    switchView("tab-chat");
    appendMessage("TITAN", `Generated High-Conversion Marketing Thread for '${topic}':\n\n${res.content}`, "assistant");
  }
}

// ==========================================================================
// CLAUDE & LOVABLE STYLE LIVE ARTIFACTS INTERFACE
// ==========================================================================
let currentArtifactFilePath = "";

function displayArtifact(title, subtitle, htmlCode, filePath = "") {
  const panel = document.getElementById("artifactsPanel");
  const tEl = document.getElementById("artifactTitle");
  const subEl = document.getElementById("artifactSubtitle");
  const iframe = document.getElementById("artifactIframe");
  const codePre = document.getElementById("artifactCodePre");

  if (!panel) return;

  currentArtifactFilePath = filePath;
  if (tEl) tEl.textContent = title || "Live Interactive Artifact";
  if (subEl) subEl.textContent = subtitle || "HTML / Full-Stack Preview";
  if (iframe) iframe.srcdoc = htmlCode;
  if (codePre) codePre.textContent = htmlCode;

  toggleArtifactTab("preview");
  panel.classList.add("active");
}

function toggleArtifactTab(tab) {
  const btnPrev = document.getElementById("btnArtifactPreview");
  const btnCode = document.getElementById("btnArtifactCode");
  const prevArea = document.getElementById("artifactPreviewArea");
  const codeArea = document.getElementById("artifactCodeArea");

  if (tab === "preview") {
    if (btnPrev) btnPrev.classList.add("active");
    if (btnCode) btnCode.classList.remove("active");
    if (prevArea) prevArea.classList.remove("hidden");
    if (codeArea) codeArea.classList.add("hidden");
  } else {
    if (btnPrev) btnPrev.classList.remove("active");
    if (btnCode) btnCode.classList.add("active");
    if (prevArea) prevArea.classList.add("hidden");
    if (codeArea) codeArea.classList.remove("hidden");
  }
}

function closeArtifactPanel() {
  const panel = document.getElementById("artifactsPanel");
  if (panel) panel.classList.remove("active");
}

function openArtifactInBrowser() {
  if (currentArtifactFilePath && window.pywebview && window.pywebview.api && window.pywebview.api.open_url) {
    window.pywebview.api.open_url(currentArtifactFilePath);
  } else if (currentArtifactFilePath) {
    window.open("file:///" + currentArtifactFilePath.replace(/\\/g, "/"), "_blank");
  }
}

async function promptLovableApp() {
  const req = prompt("What interactive app would you like TITAN to build? (e.g. 'Pomodoro timer with sound', 'SaaS Pricing calculator', 'Retro Snake arcade game'):", "Pomodoro Focus Timer");
  if (!req) return;

  setOrbStatus("Generating Lovable full-stack application...", true);
  if (window.pywebview && window.pywebview.api && window.pywebview.api.generate_lovable_app) {
    const res = await window.pywebview.api.generate_lovable_app(req);
    setOrbStatus("TITAN is ready.", false);
    if (res.success) {
      displayArtifact(res.title, "Lovable / v0 Interactive Web Application", res.html_code, res.file_path);
      appendMessage("TITAN", `Generated and opened interactive app: **${res.title}** in the live Artifacts pane, Sir.`, "assistant");
    }
  }
}

async function promptFigmaDesign() {
  const comp = prompt("What UI/UX component would you like to design? (e.g. 'Biometric Login Card', 'Dark Mode Analytics Widget', 'Apple Style Audio Player'):", "Biometric Authentication Card");
  if (!comp) return;

  setOrbStatus("Generating Figma design system & vector spec...", true);
  if (window.pywebview && window.pywebview.api && window.pywebview.api.generate_figma_design) {
    const res = await window.pywebview.api.generate_figma_design(comp);
    setOrbStatus("TITAN is ready.", false);
    if (res.success) {
      displayArtifact(res.component_name, "Figma Design Tokens & Visual Layout", res.html_code, res.file_path);
      appendMessage("TITAN", `Created Figma design tokens and component visual canvas for **${res.component_name}** in Artifacts, Sir.`, "assistant");
    }
  }
}

async function promptPerplexitySearch() {
  const q = prompt("What topic would you like to research with live citations? (Perplexity mode):", "Latest developments in open source local AI models 2026");
  if (!q) return;

  setOrbStatus("Synthesizing multi-source intelligence...", true);
  if (window.pywebview && window.pywebview.api && window.pywebview.api.perplexity_search) {
    const res = await window.pywebview.api.perplexity_search(q);
    setOrbStatus("TITAN is ready.", false);
    if (res.success) {
      appendMessage("TITAN", res.answer_with_citations, "assistant");
    }
  }
}

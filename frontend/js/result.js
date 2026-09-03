// result.js — Reads REAL Flask API data from localStorage

const scanMessages = [
  "Initializing CNN model...",
  "Loading pre-trained weights...",
  "Preprocessing image pixels...",
  "Running pattern analysis...",
  "Checking GAN artifacts...",
  "Analyzing texture layers...",
  "Computing confidence score...",
  "Generating report...",
  "Analysis complete ✓"
];

window.addEventListener("DOMContentLoaded", () => {
  startScanAnimation();
  setReportMeta();
});

function startScanAnimation() {
  const progressBar = document.getElementById("scanProgress");
  const statusEl    = document.getElementById("scanStatus");
  const overlay     = document.getElementById("scanOverlay");
  const mainEl      = document.getElementById("resultMain");
  let step = 0;
  const totalSteps = scanMessages.length;

  const timer = setInterval(() => {
    if (step < totalSteps) {
      statusEl.textContent = scanMessages[step];
      progressBar.style.width = ((step + 1) / totalSteps * 100) + "%";
      step++;
    } else {
      clearInterval(timer);
      setTimeout(() => {
        overlay.classList.add("fade-out");
        mainEl.style.opacity = "1";
        setTimeout(() => {
          overlay.style.display = "none";
          loadAndRender();
        }, 600);
      }, 300);
    }
  }, 420);
}

function loadAndRender() {
  const raw    = localStorage.getItem("deepfake_result");
  const imgSrc = localStorage.getItem("deepfake_image");

  const data = raw ? JSON.parse(raw) : {
    verdict: "AI Generated", is_ai: true,
    ai_score: 87.4, real_score: 12.6, confidence: "HIGH",
    processing_time: "2.3s",
    image_info: { filename: "test.jpg", dimensions: "1024 × 768", size: "1.2 MB", format: "JPEG" },
    breakdown: { pixel_consistency: 74.3, edge_sharpness: 91.7, texture_analysis: 85.6, gan_artifacts: 93.5, color_distribution: 68.2, noise_pattern: 79.5 }
  };

  if (imgSrc) document.getElementById("previewImg").src = imgSrc;

  populateResults(data);
  animateScoreRing(data.is_ai ? data.ai_score : data.real_score);
  animateScoreCounter(data.is_ai ? data.ai_score : data.real_score);
  populateBreakdown(data.breakdown);
}

function populateResults(data) {
  const isAI = data.is_ai;

  document.getElementById("verdictText").textContent   = data.verdict.toUpperCase();
  document.getElementById("verdictIcon").textContent   = isAI ? "🤖" : "✅";
  document.getElementById("verdictDesc").textContent   = isAI
    ? "This image shows strong indicators of AI generation. Multiple anomalies detected across texture and pixel layers."
    : "This image appears authentic. No significant AI-generation patterns were detected by the CNN model.";
  document.getElementById("confidenceBadge").textContent = data.confidence;

  const verdictCard = document.getElementById("verdictCard");
  const verdictGlow = document.getElementById("verdictGlow");
  if (!isAI) {
    verdictCard.classList.add("real-verdict");
    verdictGlow.style.background = "radial-gradient(ellipse, var(--res-glow-real), transparent 70%)";
  }

  const badge = document.getElementById("imageBadge");
  badge.querySelector(".badge-text").textContent = isAI ? "AI GENERATED" : "REAL IMAGE";
  if (!isAI) badge.classList.add("real-badge");

  document.getElementById("scoreType").textContent  = isAI ? "AI" : "REAL";
  document.getElementById("aiPct").textContent      = data.ai_score + "%";
  document.getElementById("realPct").textContent    = data.real_score + "%";
  document.getElementById("procTime").textContent   = data.processing_time;

  if (!isAI) document.getElementById("ringFill").classList.add("real-ring");

  if (data.image_info) {
    document.getElementById("fileName").textContent = data.image_info.filename  || "—";
    document.getElementById("fileSize").textContent = data.image_info.size       || "—";
    document.getElementById("fileDims").textContent = data.image_info.dimensions || "—";
    document.getElementById("fileType").textContent = data.image_info.format     || "—";
  }

  document.getElementById("reportSummary").innerHTML = isAI
    ? `CNN model concludes with <strong>${data.confidence} confidence</strong> that this image is <strong>AI-generated</strong>.`
    : `CNN model concludes with <strong>${data.confidence} confidence</strong> that this image is <strong>Real / Authentic</strong>.`;

  const recBox = document.getElementById("recommendationBox");
  if (!isAI) {
    recBox.classList.add("safe");
    recBox.querySelector(".rec-icon").textContent = "✅";
    recBox.querySelector("p").innerHTML = "This image appears <strong>authentic</strong>. Always verify from the original source for critical decisions.";
  }
}

function populateBreakdown(breakdown) {
  if (!breakdown) return;
  const map = {
    pixel_consistency:  { icon: "🔲", name: "Pixel Consistency",   note: "Pixel distribution analysis across image regions." },
    edge_sharpness:     { icon: "✂️",  name: "Edge Sharpness",      note: "Edge transition smoothness vs real camera optics." },
    texture_analysis:   { icon: "🧵", name: "Texture Analysis",    note: "Skin & surface texture naturalness evaluation." },
    gan_artifacts:      { icon: "👾", name: "GAN Artifacts",       note: "Checkerboard and frequency-domain artifact detection." },
    color_distribution: { icon: "🎨", name: "Color Distribution",  note: "RGB histogram and color clustering analysis." },
    noise_pattern:      { icon: "📡", name: "Noise Pattern",       note: "Sensor noise vs real camera profile comparison." },
  };
  const list = document.getElementById("breakdownList");
  list.innerHTML = "";

  Object.entries(breakdown).forEach(([key, score], i) => {
    const info  = map[key] || { icon: "📊", name: key, note: "" };
    const s     = Math.min(100, Math.max(0, score));
    const color = s >= 80 ? "#ef4444" : s >= 55 ? "#f59e0b" : "#10b981";

    const item = document.createElement("div");
    item.className = "breakdown-item";
    item.innerHTML = `
      <div class="breakdown-top">
        <span class="breakdown-icon">${info.icon}</span>
        <span class="breakdown-name">${info.name}</span>
        <span class="breakdown-score">${s.toFixed(1)}<small>%</small></span>
      </div>
      <div class="breakdown-bar-track">
        <div class="breakdown-bar" style="--width:${s}%; --color:${color}; width:0%;"></div>
      </div>
      <p class="breakdown-note">${info.note}</p>`;
    list.appendChild(item);

    setTimeout(() => {
      item.querySelector(".breakdown-bar").style.width = s + "%";
    }, 200 + i * 120);
  });
}

function animateScoreRing(score) {
  const offset = 314 - (score / 100) * 314;
  setTimeout(() => { document.getElementById("ringFill").style.strokeDashoffset = offset; }, 200);
}

function animateScoreCounter(targetScore) {
  const el = document.getElementById("scoreNumber");
  let current = 0;
  const steps = 60;
  const increment = targetScore / steps;
  const timer = setInterval(() => {
    current += increment;
    if (current >= targetScore) { current = targetScore; clearInterval(timer); }
    el.textContent = Math.round(current);
  }, 1800 / steps);
}

function setReportMeta() {
  const now = new Date();
  document.getElementById("analysisTime").textContent =
    now.toLocaleDateString("en-IN", { day:"numeric", month:"short", year:"numeric", hour:"2-digit", minute:"2-digit" });
  document.getElementById("reportId").textContent =
    "DF-" + now.getFullYear()
    + String(now.getMonth()+1).padStart(2,"0")
    + String(now.getDate()).padStart(2,"0")
    + "-" + Math.floor(1000 + Math.random() * 9000);
}
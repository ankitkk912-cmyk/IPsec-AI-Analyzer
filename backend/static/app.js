let currentId = null;
const $ = id => document.getElementById(id);

const fileInput = $("configFile");
const dropzone = $("dropzone");
const analyzeBtn = $("analyzeBtn");

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) {
    $("fileName").textContent = file.name;
    analyzeBtn.disabled = false;
  }
});

["dragenter","dragover"].forEach(e => dropzone.addEventListener(e, ev => {
  ev.preventDefault(); dropzone.classList.add("drag");
}));
["dragleave","drop"].forEach(e => dropzone.addEventListener(e, ev => {
  ev.preventDefault(); dropzone.classList.remove("drag");
}));
dropzone.addEventListener("drop", ev => {
  const file = ev.dataTransfer.files[0];
  if (file) {
    fileInput.files = ev.dataTransfer.files;
    $("fileName").textContent = file.name;
    analyzeBtn.disabled = false;
  }
});

analyzeBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  analyzeBtn.disabled = true;
  $("message").textContent = "Analyzing configuration…";
  try {
    const fd = new FormData();
    fd.append("config", file);
    const res = await fetch("/api/analyze", {method:"POST", body:fd});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Analysis failed");
    currentId = data.id;
    renderResult(data);
    $("message").textContent = "Analysis completed successfully.";
    $("reportBtn").disabled = false;
    $("aiBtn").disabled = false;
    loadHistory();
  } catch (err) {
    $("message").textContent = err.message;
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderResult(data) {
  $("score").textContent = data.score;
  $("risk").textContent = data.risk + " RISK";
  $("risk").className = "risk " + data.risk.toLowerCase();
  $("summary").textContent = data.summary;

  const s = data.stats;
  $("checks").textContent = s.checks;
  $("passed").textContent = s.passed;
  $("warnings").textContent = s.warnings;
  $("failed").textContent = s.failed;

  const degrees = Math.round(data.score * 3.6);
  $("score").parentElement.parentElement.style.background =
    `conic-gradient(var(--accent) ${degrees}deg, #173149 ${degrees}deg)`;

  $("findingsList").innerHTML = data.checks.map(c => `
    <div class="finding">
      <div><span class="tag ${c.status.toLowerCase()}">${c.status}</span></div>
      <div>
        <div class="finding-name">${escapeHtml(c.name)}</div>
        <div class="finding-detail">${escapeHtml(c.detail)}</div>
      </div>
      <div class="severity">${escapeHtml(c.severity)}</div>
    </div>
  `).join("");

  $("recommendations").innerHTML = data.recommendations.length
    ? data.recommendations.map(r => `
      <div class="rec">
        <b>${escapeHtml(r.priority)} · ${escapeHtml(r.title)}</b>
        <p>${escapeHtml(r.text)}</p>
      </div>`).join("")
    : `<p class="muted">No recommendations.</p>`;

  document.querySelector("#findings").scrollIntoView({behavior:"smooth"});
}

$("reportBtn").addEventListener("click", () => {
  if (currentId) window.open(`/api/report/${currentId}`, "_blank");
});

$("aiBtn").addEventListener("click", async () => {
  if (!currentId) return;
  $("modal").classList.remove("hidden");
  $("aiText").textContent = "Generating explanation…";
  try {
    const res = await fetch(`/api/ai-explain/${currentId}`, {method:"POST"});
    const data = await res.json();
    $("aiText").textContent = data.explanation || data.error || "No explanation.";
  } catch (e) {
    $("aiText").textContent = "Could not contact the AI service.";
  }
});
$("closeModal").addEventListener("click", () => $("modal").classList.add("hidden"));
$("modal").addEventListener("click", e => { if(e.target === $("modal")) $("modal").classList.add("hidden"); });

async function loadHistory() {
  const res = await fetch("/api/history");
  const rows = await res.json();
  if (!rows.length) {
    $("historyList").innerHTML = `<p class="muted">No analyses yet.</p>`;
    return;
  }
  $("historyList").innerHTML = `
    <div class="history-row header"><span>File</span><span>Score</span><span>Risk</span><span>Summary</span></div>
    ${rows.map(r => `
      <div class="history-row">
        <span>${escapeHtml(r.filename)}</span>
        <span>${r.score}/100</span>
        <span>${escapeHtml(r.risk)}</span>
        <span>${escapeHtml(r.summary)}</span>
      </div>`).join("")}`;
}
function escapeHtml(v) {
  return String(v).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch]));
}
loadHistory();

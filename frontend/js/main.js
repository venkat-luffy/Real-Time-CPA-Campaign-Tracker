async function apiGet(url) {
  const res = await fetch(url);
  return res.json();
}
async function apiPost(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body || {})
  });
  return res.json();
}
function rupee(n) { return "₹" + (Number(n||0)).toFixed(2); }

// ---------- Dashboard ----------
async function loadDashboard() {
  if (!document.getElementById("kpi-clicks")) return;

  // populate campaign selector
  const campaigns = await apiGet("/api/campaigns");
  const sel = document.getElementById("campaignSelect");
  sel.innerHTML = "";
  campaigns.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id; opt.textContent = ${c.name} (CPC ₹${c.cpc});
    sel.appendChild(opt);
  });

  // load stats
  const stats = await apiGet("/api/stats");
  const m = stats.overall || {};
  document.getElementById("kpi-clicks").textContent = m.clicks ?? 0;
  document.getElementById("kpi-conversions").textContent = m.conversions ?? 0;
  document.getElementById("kpi-cpa").textContent = rupee(m.CPA || 0);
  document.getElementById("kpi-ctr").textContent = (m.CTR || 0) + "%";

  // chart
  const ctx = document.getElementById("seriesChart");
  if (ctx) {
    const labels = stats.series.map(s => s.date.slice(5));
    const clicks = stats.series.map(s => s.clicks);
    const convs = stats.series.map(s => s.conversions);
    new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Clicks", data: clicks },
          { label: "Conversions", data: convs }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // actions
  document.getElementById("btnClick")?.addEventListener("click", async () => {
    const id = Number(sel.value);
    await apiPost("/api/click", { campaign_id: id });
    loadDashboard();
  });
  document.getElementById("btnConversion")?.addEventListener("click", async () => {
    const id = Number(sel.value);
    await apiPost("/api/conversion", { campaign_id: id, user_info: "demo" });
    loadDashboard();
  });
}

// ---------- Campaigns ----------
async function loadCampaignsPage() {
  const tableBody = document.querySelector("#campaignTable tbody");
  const btnAdd = document.getElementById("btnAddCampaign");
  if (!tableBody || !btnAdd) return;

  async function refresh() {
    const data = await apiGet("/api/campaigns");
    tableBody.innerHTML = "";
    data.forEach(c => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${c.name}</td>
        <td>${rupee(c.budget)}</td>
        <td>${rupee(c.spend)}</td>
        <td>${c.metrics.clicks}</td>
        <td>${c.metrics.conversions}</td>
        <td>${rupee(c.cpc)}</td>
        <td>${rupee(c.metrics.CPA)}</td>
        <td>${c.metrics.CTR}%</td>
      `;
      tableBody.appendChild(tr);
    });
  }

  btnAdd.addEventListener("click", async () => {
    const name = document.getElementById("cName").value.trim();
    const budget = Number(document.getElementById("cBudget").value || 0);
    const cpc = Number(document.getElementById("cCPC").value || 5);
    if (!name) { alert("Enter campaign name"); return; }
    await apiPost("/api/campaigns", { name, budget, cpc });
    document.getElementById("cName").value = "";
    document.getElementById("cBudget").value = "";
    document.getElementById("cCPC").value = "";
    refresh();
  });

  refresh();
}

// ---------- Simulation ----------
async function loadSimulationPage() {
  const btn = document.getElementById("btnSimulate");
  if (!btn) return;

  let chart;
  btn.addEventListener("click", async () => {
    const budget = Number(document.getElementById("sBudget").value || 0);
    const cpc = Number(document.getElementById("sCPC").value || 5);
    const cr = Number(document.getElementById("sCR").value || 5);
    const res = await apiPost("/api/simulate", { budget, cpc, conv_rate_pct: cr });
    if (res.error) { alert(res.error); return; }
    document.getElementById("simClicks").textContent = res.clicks;
    document.getElementById("simConversions").textContent = res.conversions;
    document.getElementById("simCPA").textContent = rupee(res.CPA);

    const ctx = document.getElementById("simChart");
    const labels = ["Clicks", "Conversions"];
    const data = [res.clicks, res.conversions];

    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ label: "Projected", data }] },
      options: { responsive: true, maintainAspectRatio: false }
    });
  });
}

// ---------- Bootstrap ----------
window.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadCampaignsPage();
  loadSimulationPage();
});
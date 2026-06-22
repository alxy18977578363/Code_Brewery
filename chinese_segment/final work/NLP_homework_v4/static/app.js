const $ = (sel) => document.querySelector(sel);
let yearChart = null;
let methodTrendChart = null;
let datasetRankChart = null;
let metricRankChart = null;
let evalChart = null;
const ANALYTICS_PALETTE = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"];
let currentTopic = "";
let currentReviewHtml = "";
let currentMermaidCode = "";
let currentImageUrls = [];
let currentPapers = [];
let currentRecords = [];
let currentReview = {};
let currentClusters = { clusters: [] };
let currentKeywordCloud = [];
let currentYearTrend = [];
let currentAnalytics = null;

window.showAnalysisModal = function(idx) {
  const record = currentRecords[idx];
  if (!record || !record.detailed_analysis) {
    alert("该论文尚未生成详评。");
    return;
  }
  document.getElementById("analysis-title").innerText = record.title;
  document.getElementById("analysis-content").innerHTML = marked.parse(record.detailed_analysis);
  document.getElementById("analysis-modal").style.display = "flex";
};

window.closeAnalysisModal = function() {
  document.getElementById("analysis-modal").style.display = "none";
};

document.getElementById("btn-close-analysis").addEventListener("click", window.closeAnalysisModal);

window.doDeepRead = async function(idx) {
  const btn = document.querySelector(`.btn-deep-read[data-idx="${idx}"]`);
  if (btn) {
    btn.innerText = "加载中...";
    btn.disabled = true;
  }
  try {
    const paper = currentPapers[idx];
    const payloadPaper = { ...paper };
    delete payloadPaper._deep_read_attempted;
    const res = await fetch("/api/deep_read_paper", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paper: payloadPaper, method: "llm" })
    });
    if (!res.ok) throw new Error("Request failed");
    const data = await res.json();
    if (data.record) {
      currentRecords[idx] = data.record;
      if (data.paper) {
        data.paper._deep_read_attempted = true;
        currentPapers[idx] = data.paper;
      } else {
        currentPapers[idx]._deep_read_attempted = true;
      }
      renderPapers(currentPapers, currentRecords);
    }
  } catch (err) {
    console.error(err);
    if (btn) btn.innerText = "精读失败";
  }
};

$("#run").addEventListener("click", run);
$("#btn-poster").addEventListener("click", showPoster);
$("#btn-close-modal").addEventListener("click", () => $("#poster-modal").hidden = true);
$("#btn-print").addEventListener("click", () => window.print());
$("#btn-eval").addEventListener("click", runEvalCompare);
$("#btn-qa").addEventListener("click", askPaperQa);
$("#qa-input").addEventListener("keypress", (e) => { if (e.key === "Enter") askPaperQa(); });
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => { if (!btn.disabled) activateTab(btn.dataset.tab); });
});

$("#btn-optimize").addEventListener("click", async () => {
  const btn = $("#btn-optimize");
  btn.disabled = true;
  btn.textContent = "优化中...";
  const level = parseInt($("#opt-level").value, 10);
  pushLog(`开始深度优化，等级：Level ${level}`);
  
  try {
    const resp = await fetch("/api/optimize_review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        draft: currentReview.text || "",
        level: level,
        records: currentRecords,
        unsupported_claims: currentReview.unsupported_claims || []
      })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({error: resp.statusText}));
      throw new Error(err.error || "请求失败");
    }
    const data = await resp.json();
    (data.logs || []).forEach(pushLog);
    currentReview.text = data.text;
    if (data.citations_used) currentReview.citations_used = data.citations_used;
    if (data.hallucinated_citations) currentReview.hallucinated_citations = data.hallucinated_citations;
    if (data.unsupported_claims) currentReview.unsupported_claims = data.unsupported_claims;
    renderReview(currentReview, currentRecords.length);
    pushLog("优化完成！");
  } catch(e) {
    pushLog("优化错误：" + e.message);
    alert("优化出错：" + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "✨ 深度审核与优化";
  }
});

mermaid.initialize({ startOnLoad: false, theme: 'default' });

async function run() {
  const topic = $("#topic").value.trim();
  if (!topic) { alert("请输入研究主题"); return; }

  const method = document.querySelector('input[name="method"]:checked').value;
  const payload = {
    topic,
    year_from: $("#year_from").value || null,
    year_to: $("#year_to").value || null,
    max_results: parseInt($("#max_results").value || "12", 10),
    method,
    deep_read: $("#deep_read").checked,
  };

  const btn = $("#run");
  btn.disabled = true; btn.textContent = "运行中…";
  resetLog();
  pushLog(`开始：主题=「${topic}」, 抽取=${method}`);

  try {
    const resp = await fetch("/api/pipeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({error: resp.statusText}));
      throw new Error(err.error || "请求失败");
    }
    const data = await resp.json();
    (data.log || []).forEach(pushLog);
    currentTopic = data.topic;
    currentImageUrls = data.papers.map(p => p.image_url).filter(url => url);
    currentPapers = data.papers.map(p => ({...p, _deep_read_attempted: $("#deep_read").checked}));
    currentRecords = data.records;
    currentReview = data.review || {};
    currentClusters = data.clusters || { clusters: [] };
    currentKeywordCloud = data.keyword_cloud || [];
    currentYearTrend = data.year_trend || [];
    currentAnalytics = data.analytics || null;
    data.papers = currentPapers; // Fix Bug 1
    render(data);
  } catch (e) {
    pushLog("错误：" + e.message);
    alert("出错：" + e.message);
  } finally {
    btn.disabled = false; btn.textContent = "一键运行";
  }
}

function resetLog() { $("#log").innerHTML = ""; }
function pushLog(msg) {
  const li = document.createElement("li");
  li.textContent = msg;
  $("#log").appendChild(li);
  $("#log-box").scrollTop = $("#log-box").scrollHeight;
}

function render(data) {
  renderPapers(data.papers, data.records);
  renderClusters(data.clusters, data.papers);
  renderWordcloud(data.keyword_cloud);
  renderYearChart(data.year_trend);
  renderAnalytics(data.analytics);
  renderReview(data.review, data.records.length);
  // 检索完成：启用结果标签页并切到「分析概览」
  ["overview", "papers", "review"].forEach((t) => {
    const b = document.querySelector(`.tab[data-tab="${t}"]`);
    if (b) b.disabled = false;
  });
  activateTab("overview");
}

function activateTab(name) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => { p.hidden = p.id !== "panel-" + name; });
  // 概览里的图表若在隐藏面板中绘制会变空白，切到概览时按存储数据重绘一次
  if (name === "overview" && currentRecords && currentRecords.length) {
    renderWordcloud(currentKeywordCloud);
    renderYearChart(currentYearTrend);
    renderAnalytics(currentAnalytics);
  }
}

function renderPapers(papers, records) {
  const tbody = $("#paper-table tbody");
  tbody.innerHTML = "";
  $("#paper-count").textContent = `共 ${papers.length} 篇`;
  const recordMap = Object.fromEntries(records.map((r) => [r.paper_id, r]));
  papers.forEach((p, i) => {
    const r = recordMap[p.paper_id] || {};
    const tr = document.createElement("tr");
    let starText = p.github_stars > 0 ? (p.github_stars >= 1000 ? (p.github_stars/1000).toFixed(1)+'k' : p.github_stars) : "";
    let codeLink = p.code_url ? `<a href="${p.code_url}" target="_blank" style="margin-left:8px; font-size:12px; color:#10b981; text-decoration:none;">[Github${starText ? ' ⭐ '+starText : ''}]</a>` : "";
    let resultsTags = (r.results || []).map(res => {
      let key = [];
      if (res.dataset) key.push(res.dataset);
      if (res.metric) key.push(res.metric);
      return `<span class="tag" style="background:#fef08a; color:#854d0e;">${escapeHtml(key.join(" - "))}: ${escapeHtml(res.value)}</span>`;
    }).join(" ");
    let methodVal = document.querySelector('input[name="method"]:checked').value;
    let deepReadBtn = "";
    if (methodVal === "llm") {
      if (p._deep_read_attempted) {
        deepReadBtn = `<button class="btn-deep-read" onclick="showAnalysisModal(${i})" style="margin-left:8px; font-size:12px; cursor:pointer; background:#f5f3ff; color:#7c3aed; border:1px solid #ddd6fe; border-radius:4px; padding:2px 6px;">📖 查看详评</button>`;
      } else {
        deepReadBtn = `<button class="btn-deep-read" data-idx="${i}" onclick="doDeepRead(${i})" style="margin-left:8px; font-size:12px; cursor:pointer; background:#eff6ff; color:#3b82f6; border:1px solid #bfdbfe; border-radius:4px; padding:2px 6px;">✨精读分析</button>`;
      }
    }
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><a href="${p.url}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a>${codeLink}${deepReadBtn}<br>
          <small style="color:#64748b">${escapeHtml((p.authors || []).slice(0, 3).join(", "))}${p.authors && p.authors.length > 3 ? " 等" : ""}</small></td>
      <td>${p.year || "-"}</td>
      <td>${p.source === "arxiv" ? "arXiv" : "S2"}</td>
      <td>${tags(r.methods, "method")}</td>
      <td>${tags(r.datasets, "dataset")}</td>
      <td>${tags(r.metrics, "metric")}${resultsTags ? '<br>'+resultsTags : ''}</td>`;
    tbody.appendChild(tr);
  });
}

function tags(arr, klass = "") {
  if (!arr || !arr.length) return "<span style='color:#94a3b8'>-</span>";
  return arr.slice(0, 5).map((t) => `<span class="tag ${klass}">${escapeHtml(t)}</span>`).join("");
}

function renderClusters(clusters, papers) {
  const box = $("#clusters");
  box.innerHTML = "";
  const titleOf = Object.fromEntries(papers.map((p, i) => [p.paper_id, `[${i + 1}] ${p.title}`]));
  (clusters.clusters || []).forEach((c, i) => {
    const div = document.createElement("div");
    div.className = "cluster";
    div.innerHTML = `
      <h4>主题 ${i + 1}：${escapeHtml(c.label)}</h4>
      <div class="terms">高频词：${(c.top_terms || []).map(escapeHtml).join(" · ")}</div>
      <ul style="margin:4px 0 0; padding-left:18px; font-size:13px;">
        ${(c.paper_ids || []).slice(0, 6).map((pid) => `<li>${escapeHtml(titleOf[pid] || pid)}</li>`).join("")}
      </ul>`;
    box.appendChild(div);
  });
}

function renderWordcloud(cloud) {
  const canvas = $("#wordcloud");
  if (!cloud || !cloud.length) {
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    return;
  }
  const list = cloud.map((c) => [c.text, Math.max(8, c.weight * 8)]);
  WordCloud(canvas, {
    list,
    gridSize: 8,
    weightFactor: 1.2,
    fontFamily: "Microsoft YaHei, PingFang SC, Arial",
    color: () => `hsl(${Math.floor(Math.random() * 240)}, 60%, 45%)`,
    backgroundColor: "#fff",
    rotateRatio: 0.2,
  });
}

function renderYearChart(trend) {
  const ctx = $("#year-chart").getContext("2d");
  if (yearChart) yearChart.destroy();
  const labels = trend.map(([y]) => y);
  const values = trend.map(([, c]) => c);
  yearChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "论文数",
        data: values,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.15)",
        tension: 0.3,
        fill: true,
      }],
    },
    options: {
      responsive: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

async function askPaperQa() {
  const input = $("#qa-input");
  const q = input.value.trim();
  if (!q) return;
  if (!currentPapers || !currentPapers.length) {
    alert("请先运行检索，得到文献列表后再提问。");
    return;
  }
  input.value = "";
  const conv = $("#qa-conversation");
  const item = document.createElement("div");
  item.className = "qa-item";
  item.innerHTML = `<div class="qa-q">🙋 ${escapeHtml(q)}</div><div class="qa-a review-md">思考中…</div>`;
  conv.appendChild(item);
  conv.scrollTop = conv.scrollHeight;
  const aDiv = item.querySelector(".qa-a");
  try {
    const resp = await fetch("/api/paper_qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, papers: currentPapers, records: currentRecords }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "请求失败");
    const total = (currentRecords || []).length;
    let html = citeSup(marked.parse(data.answer || ""), total);
    if (data.hallucinated_citations && data.hallucinated_citations.length) {
      html += `<div class="qa-warn">⚠ 检测到越界引用：[${data.hallucinated_citations.join("]、[")}]（超出 1–${total} 范围，可能是幻觉）</div>`;
    } else if (data.fallback) {
      html += `<div class="qa-warn">提示：未配置大模型，以上为关键词匹配的降级结果。</div>`;
    }
    aDiv.innerHTML = html;
  } catch (e) {
    aDiv.innerHTML = `<span style="color:#dc2626;">出错：${escapeHtml(e.message)}</span>`;
  }
  conv.scrollTop = conv.scrollHeight;
}

async function runEvalCompare() {
  const btn = $("#btn-eval");
  const withLlm = $("#eval-llm").checked;
  btn.disabled = true;
  btn.textContent = withLlm ? "评测中(含 LLM,较慢)..." : "评测中...";
  $("#eval-empty").textContent = "正在 eval/labeled.json 上运行抽取评测,请稍候...";
  $("#eval-empty").hidden = false;
  try {
    const resp = await fetch("/api/eval_compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ llm: withLlm }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "请求失败");
    if (withLlm && !data.llm) {
      $("#eval-empty").textContent = "未检测到 DEEPSEEK_API_KEY,已仅评测规则法。";
      $("#eval-empty").hidden = false;
    } else {
      $("#eval-empty").hidden = true;
    }
    renderEvalResult(data);
  } catch (e) {
    $("#eval-empty").textContent = "评测出错:" + e.message;
    $("#eval-empty").hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "运行评测";
  }
}

function renderEvalResult(data) {
  $("#eval-result").hidden = false;
  const FIELDS = [
    ["datasets_prf", "数据集"],
    ["metrics_prf", "指标"],
  ];
  // ---- 柱状图：各字段 F1 对比 ----
  const ctx = $("#eval-chart").getContext("2d");
  if (evalChart) evalChart.destroy();
  const datasets = [{
    label: "规则法",
    data: FIELDS.map(([f]) => +(data.rule[f].F1).toFixed(3)),
    backgroundColor: "#2563eb",
    borderRadius: 4,
  }];
  if (data.llm) {
    datasets.push({
      label: "LLM 法",
      data: FIELDS.map(([f]) => +(data.llm[f].F1).toFixed(3)),
      backgroundColor: "#10b981",
      borderRadius: 4,
    });
  }
  evalChart = new Chart(ctx, {
    type: "bar",
    data: { labels: FIELDS.map(([, n]) => n), datasets },
    options: {
      responsive: false,
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 12 } } },
        title: { display: true, text: `标注样本 n=${data.n}`, font: { size: 12 }, color: "#64748b" },
      },
      scales: { y: { beginAtZero: true, max: 1, ticks: { stepSize: 0.2 } } },
    },
  });
  // ---- 明细表：P/R/F1 ----
  const tbody = $("#eval-table tbody");
  tbody.innerHTML = "";
  const addRows = (summary, methodLabel, cls) => {
    FIELDS.forEach(([f, name], idx) => {
      const s = summary[f];
      const tr = document.createElement("tr");
      const head = idx === 0
        ? `<td rowspan="${FIELDS.length}" style="font-weight:600; vertical-align:top; background:${cls};">${methodLabel}</td>`
        : "";
      tr.innerHTML = `${head}<td>${name}</td><td>${s.P.toFixed(3)}</td><td>${s.R.toFixed(3)}</td><td>${s.F1.toFixed(3)}</td>`;
      tbody.appendChild(tr);
    });
  };
  addRows(data.rule, "规则法", "#eff6ff");
  if (data.llm) addRows(data.llm, "LLM 法", "#ecfdf5");
}

function renderAnalytics(a) {
  const card = $("#analytics-card");
  if (!a) { if (card) card.hidden = true; return; }
  card.hidden = false;
  renderMethodTrend(a.methods_over_time);
  datasetRankChart = renderRankBar("dataset-rank-chart", a.dataset_rank, "#0ea5e9", datasetRankChart);
  metricRankChart = renderRankBar("metric-rank-chart", a.metric_rank, "#f59e0b", metricRankChart);
  renderHotMethods(a.hot_methods, a.recent_years);
}

function renderMethodTrend(mot) {
  const ctx = $("#method-trend-chart").getContext("2d");
  if (methodTrendChart) methodTrendChart.destroy();
  if (!mot || !mot.series || !mot.series.length || !mot.years.length) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    return;
  }
  const datasets = mot.series.map((s, i) => ({
    label: s.name,
    data: s.counts,
    borderColor: ANALYTICS_PALETTE[i % ANALYTICS_PALETTE.length],
    backgroundColor: ANALYTICS_PALETTE[i % ANALYTICS_PALETTE.length] + "33",
    tension: 0.3,
    fill: false,
    borderWidth: 2,
    pointRadius: 3,
  }));
  methodTrendChart = new Chart(ctx, {
    type: "line",
    data: { labels: mot.years, datasets },
    options: {
      responsive: false,
      plugins: { legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

function renderRankBar(canvasId, rank, color, old) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  if (old) old.destroy();
  if (!rank || !rank.length) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    return null;
  }
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: rank.map((d) => d.name),
      datasets: [{ data: rank.map((d) => d.count), backgroundColor: color, borderRadius: 4 }],
    },
    options: {
      indexAxis: "y",
      responsive: false,
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

function renderHotMethods(hot, years) {
  const box = $("#hot-methods");
  const title = $("#hot-methods-title");
  if (years && years.length === 2) {
    title.textContent = `近两年热点方法（${years[0]}–${years[1]}）`;
  }
  if (!hot || !hot.length) {
    box.innerHTML = "<span style='color:#94a3b8'>暂无近两年数据</span>";
    return;
  }
  box.innerHTML = hot.map((h, i) =>
    `<span class="tag method" style="font-size:13px; margin:3px 4px 3px 0; display:inline-block;">${i + 1}. ${escapeHtml(h.name)} <b style="color:#1d4ed8;">×${h.count}</b></span>`
  ).join("");
}

function renderReview(review, totalRefs) {
  const md = review.text || "";
  // 把 [n] 引用号高亮成蓝色
  const html = marked.parse(md).replace(/\[(\d+)\]/g, (m, n) => {
    const num = parseInt(n, 10);
    const cls = num >= 1 && num <= totalRefs ? "cite" : "cite warn";
    return `<sup class="${cls}">[${n}]</sup>`;
  });
  $("#review").innerHTML = html;
  currentReviewHtml = html;
  $("#review-flag").textContent = review.fallback ? "降级版（未调 LLM）" : `LLM 综述 · 引用 ${review.citations_used.length} 篇`;
  
  currentMermaidCode = review.mermaid_code || "";
  if (currentMermaidCode) {
    $("#mermaid-container").innerHTML = `<pre class="mermaid">${currentMermaidCode}</pre>`;
    mermaid.init(undefined, $("#mermaid-container .mermaid"));
  } else {
    $("#mermaid-container").innerHTML = `<span style="color:#94a3b8">暂无演进图数据</span>`;
  }
  $("#btn-poster").hidden = false;
  $("#optimize-controls").hidden = false;

  // 演进图时间校验结果：展示已修正的时间错误数
  const timeFlag = $("#mermaid-time-flag");
  const timeIssues = review.mermaid_time_issues || [];
  if (timeIssues.length) {
    timeFlag.hidden = false;
    timeFlag.textContent = `⏱ 已自动修正 ${timeIssues.length} 处时间错误`;
    timeFlag.title = timeIssues.join("\n");
  } else if (currentMermaidCode) {
    timeFlag.hidden = false;
    timeFlag.textContent = "⏱ 时间校验通过";
  } else {
    timeFlag.hidden = true;
  }

  const halluc = $("#halluc-flag");
  if (review.hallucinated_citations && review.hallucinated_citations.length) {
    halluc.hidden = false;
    halluc.textContent = `越界引用：[${review.hallucinated_citations.join("][")}]`;
  } else {
    halluc.hidden = true;
  }

  // 张冠李戴核查：句中术语不属于其引用论文时给出提示
  const gbox = $("#grounding-box");
  const claims = review.unsupported_claims || [];
  if (claims.length) {
    const rows = claims.map((c) => `
      <li>
        <span class="grounding-terms">${c.terms.map(escapeHtml).join("、")}</span>
        未见于所引文献 [${c.cited.join("][")}]
        <div class="grounding-snippet">“${escapeHtml(c.snippet)}”</div>
      </li>`).join("");
    gbox.innerHTML = `
      <div class="grounding-title">⚠ 引用核查：${claims.length} 处疑似"张冠李戴"（术语与被引论文不符，请人工复核）</div>
      <ul class="grounding-list">${rows}</ul>`;
    gbox.hidden = false;
  } else {
    gbox.innerHTML = "";
    gbox.hidden = true;
  }
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, (c) => (
    {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]
  ));
}

const SECTION_ICONS = {
  "研究背景": "📌", "主要方法分类": "🧩", "各类方法对比": "⚖️",
  "研究空白": "🕳️", "未来方向": "🚀",
};

function parseReviewSections(md) {
  if (!md) return [];
  const parts = md.split(/^##\s+/m).map((s) => s.trim()).filter(Boolean);
  return parts.map((p) => {
    const nl = p.indexOf("\n");
    if (nl === -1) return { title: p.trim(), body: "" };
    return { title: p.slice(0, nl).trim(), body: p.slice(nl + 1).trim() };
  });
}

function citeSup(html, totalRefs) {
  return html.replace(/\[(\d+)\]/g, (m, n) => {
    const num = parseInt(n, 10);
    const cls = num >= 1 && num <= totalRefs ? "cite" : "cite warn";
    return `<sup class="${cls}">[${n}]</sup>`;
  });
}

function showPoster() {
  const canvas = $("#poster-canvas");
  const papers = currentPapers || [];
  const records = currentRecords || [];
  const totalRefs = papers.length;

  // —— 元信息与统计 ——
  const years = papers.map((p) => p.year).filter(Boolean);
  const yearSpan = years.length ? `${Math.min(...years)}–${Math.max(...years)}` : "—";
  const clusters = (currentClusters && currentClusters.clusters) || [];
  const methodSet = new Set();
  records.forEach((r) => (r.methods || []).forEach((m) => methodSet.add(m)));
  const today = new Date().toLocaleDateString("zh-CN");
  const methodLabel = (document.querySelector('input[name="method"]:checked') || {}).value === "llm"
    ? "LLM 抽取" : "规则抽取";

  const stats = [
    { num: papers.length, label: "篇文献" },
    { num: yearSpan, label: "年份跨度" },
    { num: clusters.length || "—", label: "研究主题" },
    { num: methodSet.size, label: "方法 / 模型" },
  ];
  const statsHtml = stats.map((s) =>
    `<div class="pstat"><div class="pstat-num">${escapeHtml(String(s.num))}</div><div class="pstat-label">${s.label}</div></div>`
  ).join("");

  // —— 综述分节卡 ——
  const sections = parseReviewSections((currentReview && currentReview.text) || "");
  let sectionCards;
  if (sections.length) {
    sectionCards = sections.map((s) => `
      <div class="pcard">
        <h3>${SECTION_ICONS[s.title] || "▍"} ${escapeHtml(s.title)}</h3>
        <div class="review-md">${citeSup(marked.parse(s.body), totalRefs)}</div>
      </div>`).join("");
  } else {
    sectionCards = `<div class="pcard"><div class="review-md">${currentReviewHtml}</div></div>`;
  }

  // —— 关键词标签 ——
  const kw = (currentKeywordCloud || []).slice(0, 18);
  const kwHtml = kw.length ? `
    <div class="pcard"><h3>🔑 高频关键词</h3>
      <div class="ptags">${kw.map((k) =>
        `<span class="ptag" style="font-size:${Math.min(22, 12 + (k.weight || 1))}px">${escapeHtml(k.text)}</span>`
      ).join("")}</div>
    </div>` : "";

  // —— 主题聚类卡 ——
  const numOf = {};
  papers.forEach((p, i) => { numOf[p.paper_id] = i + 1; });
  const clusterHtml = clusters.length ? `
    <div class="pcard"><h3>🗂 研究主题聚类</h3>
      ${clusters.map((c, i) => `
        <div class="pcluster">
          <div class="pcluster-name">主题 ${i + 1}：${escapeHtml(c.label)}</div>
          <div class="pcluster-terms">${(c.top_terms || []).slice(0, 6).map(escapeHtml).join(" · ")}</div>
          <div class="pcluster-refs">${(c.paper_ids || []).map((pid) => numOf[pid]).filter(Boolean).map((n) => `[${n}]`).join(" ")}</div>
        </div>`).join("")}
    </div>` : "";

  // —— 演进图占位 ——
  const mermaidHtml = currentMermaidCode
    ? `<div class="pcard"><h3>🧬 算法演进路线</h3><div id="poster-mermaid-box" class="pmermaid"></div></div>` : "";

  // —— 代表性配图 ——
  const imgs = (currentImageUrls || []).slice(0, 2);
  const imgHtml = imgs.length ? `
    <div class="pcard"><h3>🖼 代表性图示</h3>
      <div class="pimgs">${imgs.map((u) => `<img src="${escapeHtml(u)}" alt="paper figure" />`).join("")}</div>
    </div>` : "";

  // —— 参考文献 ——
  const refsHtml = papers.length ? `
    <div class="pcard pcard-full"><h3>📚 参考文献</h3>
      <ol class="prefs">
        ${papers.map((p) => {
          const a = (p.authors || []).slice(0, 3).join(", ") + ((p.authors || []).length > 3 ? " 等" : "");
          const star = p.github_stars > 0
            ? ` · ⭐${p.github_stars >= 1000 ? (p.github_stars / 1000).toFixed(1) + "k" : p.github_stars}` : "";
          return `<li><a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a>` +
                 `<span class="pref-meta">${escapeHtml(a)}${p.year ? ` (${p.year})` : ""}${star}</span></li>`;
        }).join("")}
      </ol>
    </div>` : "";

  canvas.innerHTML = `
    <div class="poster-banner">
      <div class="poster-banner-tag">文献综述 · 学术海报</div>
      <h1>${escapeHtml(currentTopic || "未命名主题")}</h1>
      <div class="poster-meta">生成日期 ${today} · ${methodLabel} · 数据来源 arXiv / Semantic Scholar</div>
    </div>
    <div class="poster-stats">${statsHtml}</div>
    <div class="poster-grid">
      <div class="poster-main">${sectionCards}</div>
      <div class="poster-side">${kwHtml}${clusterHtml}${mermaidHtml}${imgHtml}</div>
    </div>
    ${refsHtml}
    <div class="poster-foot">本海报由文献综述 Agent 自动生成 · 引用编号 [n] 对应参考文献列表 · 仅供学术汇报参考</div>
  `;

  if (currentMermaidCode) {
    const box = document.getElementById("poster-mermaid-box");
    mermaid.render("poster-mmd-" + Date.now(), currentMermaidCode)
      .then((res) => { if (box) box.innerHTML = res.svg; })
      .catch(() => { if (box) box.innerHTML = `<pre class="mermaid">${escapeHtml(currentMermaidCode)}</pre>`; });
  }

  $("#poster-modal").hidden = false;
}

// ================= AI 选题助手 =================
let chatHistory = [];

function parseChatReply(text) {
  let html = escapeHtml(text).replace(/\n/g, "<br>");
  html = html.replace(/【(.*?)】/g, (m, k) => {
    return `<button onclick="useKeyword('${k}')" style="background:#fef08a; border:1px solid #ca8a04; color:#854d0e; padding:2px 6px; border-radius:4px; cursor:pointer; font-size:13px; font-weight:bold; margin: 2px;">一键填入：${k}</button>`;
  });
  return html;
}

window.useKeyword = function(k) {
  $("#topic").value = k;
  $("#assistant-modal").hidden = true;
  $("#topic").style.background = "#fef08a";
  setTimeout(() => $("#topic").style.background = "", 800);
};

function appendChatMsg(role, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + role;
  div.innerHTML = parseChatReply(text);
  $("#chat-box").appendChild(div);
  $("#chat-box").scrollTop = $("#chat-box").scrollHeight;
  return div;
}

async function sendChatMessage() {
  const input = $("#chat-input");
  const text = input.value.trim();
  if (!text) return;
  
  input.value = "";
  appendChatMsg("user", text);
  chatHistory.push({ role: "user", content: text });
  
  const aiMsgDiv = appendChatMsg("ai", "思考中...");
  
  try {
    const res = await fetch("/api/chat_assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: chatHistory })
    });
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    
    aiMsgDiv.innerHTML = parseChatReply(data.reply);
    chatHistory.push({ role: "assistant", content: data.reply });
  } catch(e) {
    aiMsgDiv.innerText = "抱歉，出错了：" + e.message;
    chatHistory.pop(); // 回退用户的提问
  }
}

$("#btn-open-assistant").addEventListener("click", () => {
  $("#assistant-modal").hidden = false;
  setTimeout(() => $("#chat-input").focus(), 100);
});

$("#btn-close-assistant").addEventListener("click", () => {
  $("#assistant-modal").hidden = true;
});

$("#btn-chat-send").addEventListener("click", sendChatMessage);
$("#chat-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendChatMessage();
});


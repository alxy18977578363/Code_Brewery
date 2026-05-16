const P_COLORS = {
    leaf: "#2f6b45",
    leaf_light: "#8cb369",
    turmeric: "#d89a24",
    sambar: "#b85c38",
    rose: "#d9718c",
    marina: "#1e6f8c",
    steel: "#596c76",
    ink: "#2b2522",
    muted: "#766b60",
    grid: "#e4d5c2",
    cream: "#f6ecd8",
    charcoal: "#1f1b18",
};

const CHENNAI_SCALE = [
    [0, "#f6ecd8"],
    [0.2, "#f1c46b"],
    [0.45, "#d89a24"],
    [0.7, "#b85c38"],
    [1.0, "#6d2f20"],
];

const ERROR_SCALE = [
    [0, "#1e6f8c"],
    [0.5, "#f6ecd8"],
    [1.0, "#d9718c"],
];

const PLOTLY_LAYOUT_BASE = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
};

// ── Data Loading ──

async function loadPredictionData() {
    const resp = await fetch("/api/prediction-analysis");
    if (!resp.ok) throw new Error(`Failed: ${resp.status}`);
    return resp.json();
}

// ── Audit Tables ──

function buildFeatureAudit(payload) {
    const el = document.getElementById("feature-audit-table");
    if (!el) return;
    const rows = payload.meta.feature_blocks.map((b) =>
        `<tr><td style="font-weight:600">${b.block}</td><td>${b.count}</td><td>${b.cols.join(", ")}</td></tr>`
    ).join("");
    el.innerHTML = `
        <table class="data-table">
            <thead><tr><th>Feature Block</th><th>Columns</th><th>Notes</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

function buildSplitAudit(payload) {
    const el = document.getElementById("split-audit-table");
    if (!el) return;
    const s = payload.split_audit;
    const items = [
        ["Train rows", s.train_rows.toLocaleString()],
        ["Test rows", s.test_rows.toLocaleString()],
        ["Train unique names", s.train_unique_names.toLocaleString()],
        ["Test unique names", s.test_unique_names.toLocaleString()],
        ["Train mean rating", s.train_mean.toFixed(4)],
        ["Test mean rating", s.test_mean.toFixed(4)],
    ];
    el.innerHTML = `
        <table class="data-table">
            <thead><tr><th>Metric</th><th>Value</th></tr></thead>
            <tbody>${items.map(([k, v]) => `<tr><td>${k}</td><td style="font-family:monospace">${v}</td></tr>`).join("")}</tbody>
        </table>`;
}

// ── Leaderboard ──

function buildLeaderboardChart(payload) {
    const lb = payload.leaderboard.slice().reverse();
    const models = lb.map((r) => r.model);
    const maeTest = lb.map((r) => r.mae_test);
    const maeTrain = lb.map((r) => r.mae_train);
    const colors = lb.map((r) => r.is_best ? P_COLORS.leaf : P_COLORS.sambar);

    const traceTest = {
        type: "bar", orientation: "h", name: "Test MAE",
        y: models, x: maeTest, marker: { color: colors, opacity: 0.92 },
    };
    const traceTrain = {
        type: "bar", orientation: "h", name: "Train MAE",
        y: models, x: maeTrain.map((v) => v !== null ? v : 0),
        marker: { color: colors.map((c) => c + "55") },
    };

    const layout = {
        barmode: "group",
        margin: { l: 160, r: 60, t: 12, b: 48 },
        xaxis: { title: "MAE (rating points)", gridcolor: P_COLORS.grid },
        yaxis: { automargin: true },
        legend: { orientation: "h", y: 1.12 },
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("leaderboard-chart", [traceTest, traceTrain], layout, { responsive: true });
}

// ── Residual Hexbin ──

function buildResidualHexbin(payload) {
    const hb = payload.residual_anatomy.hexbin;
    const xCenters = hb.x_edges.slice(0, -1).map((e, i) => (e + hb.x_edges[i + 1]) / 2);
    const yCenters = hb.y_edges.slice(0, -1).map((e, i) => (e + hb.y_edges[i + 1]) / 2);

    const trace = {
        type: "heatmap", z: hb.counts, x: xCenters, y: yCenters,
        colorscale: CHENNAI_SCALE,
        hovertemplate: "Actual: %{x:.2f}<br>Predicted: %{y:.2f}<br>Count: %{z}<extra></extra>",
        colorbar: { title: "Test rows" },
    };

    const layout = {
        margin: { l: 56, r: 18, t: 12, b: 48 },
        xaxis: { title: "Actual rating", range: [0, 5], gridcolor: P_COLORS.grid },
        yaxis: { title: "Predicted rating", range: [0, 5], gridcolor: P_COLORS.grid },
        shapes: [{
            type: "line", x0: 0, x1: 5, y0: 0, y1: 5,
            line: { color: P_COLORS.rose, width: 1.4, dash: "dash" },
        }],
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("hexbin-chart", [trace], layout, { responsive: true });
}

// ── Residual Histogram ──

function buildResidualHistogram(payload) {
    const h = payload.residual_anatomy.histogram;
    const centers = h.bin_edges.slice(0, -1).map((e, i) => (e + h.bin_edges[i + 1]) / 2);
    const colors = centers.map((c) => c < 0 ? P_COLORS.marina : P_COLORS.rose);

    const trace = {
        type: "bar", x: centers, y: h.counts,
        marker: { color: colors, opacity: 0.78, line: { color: P_COLORS.cream, width: 0.7 } },
        hovertemplate: "Residual: %{x:.2f}<br>Count: %{y}<extra></extra>",
    };

    const layout = {
        margin: { l: 52, r: 18, t: 12, b: 48 },
        xaxis: { title: "Residual (actual - predicted)", gridcolor: P_COLORS.grid },
        yaxis: { title: "Test rows", gridcolor: P_COLORS.grid },
        shapes: [{
            type: "line", x0: 0, x1: 0, y0: 0, y1: 1, yref: "paper",
            line: { color: P_COLORS.ink, width: 1.4 },
        }],
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("residual-hist-chart", [trace], layout, { responsive: true });
}

// ── Error by Segment ──

function buildErrorBySegment(payload) {
    const data = payload.error_by_segment.slice().reverse();
    const biasMin = Math.min(...data.map((d) => d.bias));
    const biasMax = Math.max(...data.map((d) => d.bias));
    const biasRange = biasMax - biasMin || 1;

    const trace = {
        type: "bar", orientation: "h",
        y: data.map((d) => d.segment),
        x: data.map((d) => d.mae),
        marker: {
            color: data.map((d) => {
                const t = (d.bias - biasMin) / biasRange;
                if (t < 0.4) return P_COLORS.marina;
                if (t > 0.6) return P_COLORS.rose;
                return P_COLORS.steel;
            }),
            opacity: 0.88,
        },
        text: data.map((d) => `${d.mae.toFixed(3)} | bias=${d.bias.toFixed(3)} | n=${d.count}`),
        textposition: "outside",
        textfont: { size: 9, color: P_COLORS.muted },
    };

    const layout = {
        margin: { l: 160, r: 100, t: 12, b: 48 },
        xaxis: { title: "MAE", gridcolor: P_COLORS.grid },
        yaxis: { automargin: true },
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("error-segment-chart", [trace], layout, { responsive: true });
}

// ── Error by Area ──

function buildErrorByArea(payload) {
    const data = payload.error_by_area.slice().reverse();
    const biasMin = Math.min(...data.map((d) => d.bias));
    const biasMax = Math.max(...data.map((d) => d.bias));
    const biasRange = biasMax - biasMin || 1;

    const trace = {
        type: "bar", orientation: "h",
        y: data.map((d) => d.area),
        x: data.map((d) => d.mae),
        marker: {
            color: data.map((d) => {
                const t = (d.bias - biasMin) / biasRange;
                if (t < 0.4) return P_COLORS.marina;
                if (t > 0.6) return P_COLORS.rose;
                return P_COLORS.steel;
            }),
            opacity: 0.84,
        },
        text: data.map((d) => `${d.mae.toFixed(3)} | n=${d.count}`),
        textposition: "outside",
        textfont: { size: 9, color: P_COLORS.muted },
    };

    const layout = {
        margin: { l: 140, r: 90, t: 12, b: 48 },
        xaxis: { title: "MAE", gridcolor: P_COLORS.grid },
        yaxis: { automargin: true },
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("error-area-chart", [trace], layout, { responsive: true });
}

// ── Permutation Importance ──

function buildPermutationImportance(payload) {
    const data = payload.permutation_importance.slice().reverse();
    const scaleMax = Math.max(...data.map((d) => d.importance_mean + d.importance_std));

    const trace = {
        type: "bar", orientation: "h",
        y: data.map((d) => d.feature),
        x: data.map((d) => d.importance_mean),
        error_x: { type: "data", array: data.map((d) => d.importance_std), symmetric: true, color: P_COLORS.muted, thickness: 1.5 },
        marker: {
            color: data.map((_, i) => {
                const t = i / Math.max(data.length - 1, 1);
                return `rgb(${Math.round(47 + t * 127)}, ${Math.round(107 - t * 75)}, ${Math.round(69 - t * 17)})`;
            }),
            opacity: 0.92,
        },
    };

    const layout = {
        margin: { l: 180, r: 24, t: 12, b: 48 },
        xaxis: { title: "MAE increase after shuffle", gridcolor: P_COLORS.grid, range: [0, scaleMax * 1.2] },
        yaxis: { automargin: true },
        ...PLOTLY_LAYOUT_BASE,
    };

    Plotly.newPlot("perm-importance-chart", [trace], layout, { responsive: true });
}

// ── Ridge Coefficients ──

function buildRidgeCoefficients(payload) {
    const pos = payload.ridge_coefficients.positive;
    const neg = payload.ridge_coefficients.negative;

    function lollipopTrace(items, color) {
        const names = items.map((d) => d.feature);
        const vals = items.map((d) => d.coefficient);
        const stemX = [];
        const stemY = [];
        names.forEach((n, i) => {
            stemX.push(0, vals[i], null);
            stemY.push(n, n, null);
        });
        const stem = {
            type: "scatter", mode: "lines", x: stemX, y: stemY,
            line: { color: color, width: 3 }, showlegend: false, hoverinfo: "skip",
        };
        const dot = {
            type: "scatter", mode: "markers", x: vals, y: names,
            marker: { color: color, size: 9, line: { color: P_COLORS.ink, width: 0.5 } },
            showlegend: false,
        };
        return [stem, dot];
    }

    // Negative panel
    const negTraces = lollipopTrace(neg, P_COLORS.marina);
    const negLayout = {
        margin: { l: 180, r: 24, t: 40, b: 48 },
        xaxis: { title: "Ridge coefficient", gridcolor: P_COLORS.grid },
        yaxis: { autorange: "reversed" },
        title: { text: "Lower-rating associations", font: { size: 13, color: P_COLORS.ink } },
        ...PLOTLY_LAYOUT_BASE,
    };
    Plotly.newPlot("ridge-coef-chart", [], {}, { responsive: true }).then(() => {
        // Two-panel via domain
        const posTraces = lollipopTrace(pos, P_COLORS.leaf);
        const allTraces = [
            ...negTraces.map((t) => ({ ...t, xaxis: "x", yaxis: "y" })),
            ...posTraces.map((t) => ({ ...t, xaxis: "x2", yaxis: "y2" })),
        ];
        const layout = {
            grid: { rows: 1, columns: 2, pattern: "independent" },
            xaxis: { title: "Negative coeff", domain: [0, 0.47], gridcolor: P_COLORS.grid },
            yaxis: { automargin: true },
            xaxis2: { title: "Positive coeff", domain: [0.53, 1], gridcolor: P_COLORS.grid },
            yaxis2: { automargin: true },
            margin: { l: 180, r: 24, t: 12, b: 48 },
            annotations: [
                { x: 0.23, y: 1.05, xref: "paper", yref: "paper", text: "<b>Lower-rating</b>", showarrow: false, font: { size: 11, color: P_COLORS.marina } },
                { x: 0.77, y: 1.05, xref: "paper", yref: "paper", text: "<b>Higher-rating</b>", showarrow: false, font: { size: 11, color: P_COLORS.leaf } },
            ],
            ...PLOTLY_LAYOUT_BASE,
        };
        Plotly.newPlot("ridge-coef-chart", allTraces, layout, { responsive: true });
    });
}

// ── Partial Dependence ──

function buildPdpLineChart(elId, data, title, xTitle, color) {
    const trace = {
        type: "scatter", mode: "lines+markers",
        x: data.x_values, y: data.y_values,
        line: { color: color, width: 2.4 },
        marker: { color: color, size: 7, line: { color: P_COLORS.ink, width: 0.5 } },
    };
    const layout = {
        margin: { l: 56, r: 16, t: 36, b: 48 },
        xaxis: { title: xTitle, gridcolor: P_COLORS.grid },
        yaxis: { title: "Mean predicted rating", gridcolor: P_COLORS.grid },
        title: { text: title, font: { size: 12, color: P_COLORS.ink }, x: 0.02, xanchor: "left" },
        ...PLOTLY_LAYOUT_BASE,
    };
    Plotly.newPlot(elId, [trace], layout, { responsive: true });
}

function buildPartialDependence(payload) {
    const pdp = payload.partial_dependence;
    buildPdpLineChart("pdp-brand-chart", pdp.brand_footprint, "Brand Footprint Curve", "Same-name outlet count", P_COLORS.leaf);
    buildPdpLineChart("pdp-distance-chart", pdp.location_distance, "Location-Distance Curve", "Distance from city-median (km)", P_COLORS.sambar);
    buildPdpLineChart("pdp-dish-chart", pdp.menu_description, "Menu-Description Curve", "Number of top-dish tokens", P_COLORS.marina);

    // Segment PD bar
    const seg = pdp.segment_partial;
    const trace = {
        type: "bar", orientation: "h",
        y: seg.map((d) => d.segment),
        x: seg.map((d) => d.prediction),
        marker: {
            color: seg.map((_, i) => {
                const t = i / Math.max(seg.length - 1, 1);
                return `rgb(${Math.round(47 + t * 147)}, ${Math.round(107 - t * 67)}, ${Math.round(69 + t * 11)})`;
            }),
            opacity: 0.92,
        },
        text: seg.map((d) => d.prediction.toFixed(3)),
        textposition: "outside",
        textfont: { size: 9, color: P_COLORS.muted },
    };
    const layout = {
        margin: { l: 160, r: 60, t: 36, b: 48 },
        xaxis: { title: "Mean predicted rating", gridcolor: P_COLORS.grid },
        yaxis: { automargin: true },
        title: { text: "Segment Partial Dependence", font: { size: 12, color: P_COLORS.ink }, x: 0.02, xanchor: "left" },
        ...PLOTLY_LAYOUT_BASE,
    };
    Plotly.newPlot("pdp-segment-chart", [trace], layout, { responsive: true });
}

// ── Worst Misses Table ──

function buildWorstMissesTable(payload) {
    const el = document.getElementById("worst-misses-table");
    if (!el) return;
    const rows = payload.worst_misses.map((r, i) => {
        const errColor = r.abs_error > 1.0 ? "#d9718c" : r.abs_error > 0.5 ? "#d89a24" : "#2f6b45";
        return `<tr>
            <td>${i + 1}</td>
            <td>${r.restaurant}</td>
            <td>${r.segment}</td>
            <td>${r.area}</td>
            <td style="font-family:monospace">${r.actual.toFixed(1)}</td>
            <td style="font-family:monospace">${r.predicted.toFixed(3)}</td>
            <td style="font-family:monospace;color:${errColor};font-weight:600">${r.residual.toFixed(3)}</td>
            <td style="font-family:monospace;color:${errColor}">${r.abs_error.toFixed(3)}</td>
        </tr>`;
    }).join("");
    el.innerHTML = `
        <table class="data-table">
            <thead><tr><th>#</th><th>Restaurant</th><th>Segment</th><th>Area</th><th>Actual</th><th>Predicted</th><th>Residual</th><th>Abs Error</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

// ── Main Render ──

async function renderPredictionPage() {
    const hint = document.getElementById("loading-hint");
    const table = document.getElementById("analysis-table");
    if (!hint || !table) return;

    try {
        const payload = await loadPredictionData();

        hint.style.display = "none";
        table.style.display = "";

        buildFeatureAudit(payload);
        buildSplitAudit(payload);
        buildLeaderboardChart(payload);
        buildResidualHexbin(payload);
        buildResidualHistogram(payload);
        buildErrorBySegment(payload);
        buildErrorByArea(payload);
        buildPermutationImportance(payload);
        buildRidgeCoefficients(payload);
        buildPartialDependence(payload);
        buildWorstMissesTable(payload);
    } catch (error) {
        console.error(error);
        hint.innerHTML = "Failed to load prediction analysis data.";
    }
}

document.addEventListener("DOMContentLoaded", renderPredictionPage);

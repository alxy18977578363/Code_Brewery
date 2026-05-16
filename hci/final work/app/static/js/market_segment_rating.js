async function loadMarketSegmentRatingData() {
    const response = await fetch("/api/market-segment-rating");
    if (!response.ok) {
        throw new Error(`Failed to load data: ${response.status}`);
    }
    return response.json();
}

function buildRidgelineChart(payload) {
    const host = document.getElementById("ridgeline-chart");
    if (!host) return;

    const { centers, records } = payload.ridgeline;
    const traces = [];
    const annotations = [];

    const segmentColors = {
        "Restaurant": "#2f6b45",
        "Fast Food": "#d89a24",
        "Cloud Kitchen": "#1e6f8c",
        "Hotel": "#b85c38",
        "Cafe": "#d9718c",
        "Bakery & Sweet Shop": "#766b60",
        "Bar": "#596c76",
        "Ice Cream Parlour": "#8cb369",
    };

    records.forEach((rec, idx) => {
        const baseline = idx * 0.86;
        const color = segmentColors[rec.segment] || "#999999";
        const yVals = rec.densities.map((d) => baseline + d);
        const baselineVals = centers.map(() => baseline);

        // invisible baseline trace (fill anchor)
        traces.push({
            type: "scatter",
            mode: "lines",
            x: centers,
            y: baselineVals,
            line: { color: "transparent", width: 0 },
            showlegend: false,
            hoverinfo: "skip",
        });

        // density trace filled to previous (baseline)
        traces.push({
            type: "scatter",
            mode: "lines",
            name: rec.segment,
            x: centers,
            y: yVals,
            fill: "tonexty",
            fillcolor: color + "99",
            line: { color: "#2b2522", width: 0.7 },
            showlegend: false,
        });

        // median marker line
        traces.push({
            type: "scatter",
            mode: "lines",
            x: [rec.median, rec.median],
            y: [baseline, baseline + 0.18],
            line: { color: "#2b2522", width: 1.6 },
            showlegend: false,
            hoverinfo: "skip",
        });

        annotations.push({
            x: 0.12,
            y: baseline + 0.18,
            xref: "paper",
            yref: "y",
            text: `<b>${rec.segment}</b>  n=${rec.count.toLocaleString()}`,
            showarrow: false,
            font: { size: 10, color: "#2b2522" },
            align: "left",
        });
    });

    const layout = {
        margin: { l: 160, r: 24, t: 12, b: 48 },
        xaxis: {
            title: "Dining Rating",
            range: [0, 5.02],
            gridcolor: "#e4d5c2",
        },
        yaxis: {
            showticklabels: false,
            showgrid: false,
            zeroline: false,
        },
        annotations: annotations,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("ridgeline-chart", traces, layout, { responsive: true });
}

function buildGroupedBarChart(payload) {
    const { segments, bands, records } = payload.grouped_bar;

    const bandColors = {
        fragile: "#8c2d04",
        developing: "#d95f0e",
        solid: "#fe9929",
        strong: "#fec44f",
        elite: "#fff7bc",
    };

    const lookup = {};
    records.forEach((r) => {
        if (!lookup[r.segment]) lookup[r.segment] = {};
        lookup[r.segment][r.band] = r.count;
    });

    const traces = bands.map((band) => ({
        type: "bar",
        name: band,
        x: segments,
        y: segments.map((s) => (lookup[s] && lookup[s][band]) || 0),
        marker: { color: bandColors[band] || "#cccccc" },
    }));

    const layout = {
        barmode: "group",
        bargap: 0.2,
        bargroupgap: 0.06,
        margin: { l: 52, r: 12, t: 12, b: 130 },
        xaxis: {
            title: "Market Segment",
            tickangle: -35,
        },
        yaxis: {
            title: "Restaurant Count",
            gridcolor: "#e4d5c2",
        },
        legend: {
            orientation: "h",
            y: 1.15,
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("grouped-bar-chart", traces, layout, { responsive: true });
}

function buildHeatmapChart(payload) {
    const { segments, features, records } = payload.heatmap;

    const lookup = {};
    records.forEach((r) => {
        const key = r.segment + "||" + r.feature;
        lookup[key] = r.share;
    });

    const z = segments.map((seg) =>
        features.map((feat) => lookup[seg + "||" + feat] || 0)
    );

    const text = z.map((row) =>
        row.map((val) => (val >= 0.22 ? (val * 100).toFixed(0) + "%" : ""))
    );

    const trace = {
        type: "heatmap",
        z: z,
        x: features,
        y: segments,
        text: text,
        texttemplate: "%{text}",
        textfont: { size: 9 },
        colorscale: [
            [0.0, "#f6ecd8"],
            [0.2, "#f1c46b"],
            [0.45, "#d89a24"],
            [0.7, "#b85c38"],
            [1.0, "#6d2f20"],
        ],
        hovertemplate: "<b>%{y}</b><br>Feature: %{x}<br>Share: %{z:.1%}<extra></extra>",
        colorbar: {
            title: "Adoption Rate",
            tickformat: ".0%",
        },
    };

    const layout = {
        margin: { l: 140, r: 80, t: 12, b: 120 },
        xaxis: {
            tickangle: -43,
            tickfont: { size: 10 },
        },
        yaxis: {
            tickfont: { size: 10 },
            autorange: "reversed",
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("heatmap-chart", [trace], layout, { responsive: true });
}

function buildCuisineTopChart(payload) {
    const records = payload.cuisine_top;
    const names = records.map((r) => r.cuisine);
    const outlets = records.map((r) => r.outlets);
    const ratings = records.map((r) => r.avg_rating);
    const isLocal = records.map((r) => r.is_local);

    const maxOutlet = Math.max(...outlets);

    // horizontal bar trace
    const barTrace = {
        type: "bar",
        orientation: "h",
        y: names,
        x: outlets,
        marker: {
            color: isLocal.map((v) => (v ? "#2f6b45" : "#d89a24")),
            opacity: 0.92,
        },
        hovertemplate: "<b>%{y}</b><br>Outlets: %{x}<br>Avg Rating: %{customdata:.2f}<extra></extra>",
        customdata: ratings,
        showlegend: false,
    };

    // avg rating dot trace (secondary x-axis)
    const dotTrace = {
        type: "scatter",
        mode: "markers",
        y: names,
        x: ratings,
        xaxis: "x2",
        marker: {
            color: "#d9718c",
            size: 9,
            line: { color: "#2b2522", width: 0.5 },
        },
        hovertemplate: "<b>%{y}</b><br>Avg Rating: %{x:.2f}<extra></extra>",
        showlegend: false,
    };

    const layout = {
        margin: { l: 140, r: 60, t: 12, b: 48 },
        xaxis: {
            title: "Tagged Outlets",
            domain: [0, 0.78],
            gridcolor: "#e4d5c2",
        },
        xaxis2: {
            title: "Mean Rating",
            domain: [0.82, 1],
            anchor: "x2",
            range: [3.0, Math.max(4.5, Math.max(...ratings) + 0.1)],
            gridcolor: "#e4d5c2",
            titlefont: { color: "#d9718c" },
            tickfont: { color: "#d9718c" },
        },
        yaxis: {
            autorange: "reversed",
            gridcolor: "#e4d5c2",
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("cuisine-top-chart", [barTrace, dotTrace], layout, { responsive: true });
}

function buildDishTopChart(payload) {
    const records = payload.dish_top;
    const names = records.map((r) => r.dish);
    const outlets = records.map((r) => r.outlets);
    const isLocal = records.map((r) => r.is_local);

    // lollipop stems: interleave 0 and outlet values separated by null
    const stemX = [];
    const stemY = [];
    names.forEach((name, i) => {
        stemX.push(0, outlets[i], null);
        stemY.push(name, name, null);
    });

    const stemTrace = {
        type: "scatter",
        mode: "lines",
        x: stemX,
        y: stemY,
        line: { color: "#c4b8b0", width: 3 },
        showlegend: false,
        hoverinfo: "skip",
    };

    // dots
    const dotTrace = {
        type: "scatter",
        mode: "markers",
        y: names,
        x: outlets,
        marker: {
            color: isLocal.map((v) => (v ? "#b85c38" : "#1e6f8c")),
            size: 11,
            line: { color: "#2b2522", width: 0.7 },
        },
        hovertemplate: "<b>%{y}</b><br>Outlets: %{x}<extra></extra>",
        showlegend: false,
    };

    const layout = {
        margin: { l: 160, r: 24, t: 12, b: 48 },
        xaxis: {
            title: "Tagged Outlets",
            gridcolor: "#e4d5c2",
        },
        yaxis: {
            autorange: "reversed",
            gridcolor: "#e4d5c2",
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("dish-top-chart", [stemTrace, dotTrace], layout, { responsive: true });
}

async function renderMarketSegmentRatingPage() {
    const host = document.getElementById("ridgeline-chart");
    if (!host) return;

    try {
        const payload = await loadMarketSegmentRatingData();
        buildRidgelineChart(payload);
        buildGroupedBarChart(payload);
        buildHeatmapChart(payload);
        buildCuisineTopChart(payload);
        buildDishTopChart(payload);
    } catch (error) {
        console.error(error);
        host.innerHTML = "Failed to load market segment data.";
    }
}

document.addEventListener("DOMContentLoaded", renderMarketSegmentRatingPage);

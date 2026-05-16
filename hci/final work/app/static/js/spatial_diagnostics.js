async function loadAreaAtlasData() {
    const response = await fetch("/api/spatial-diagnostics");

    if (!response.ok) {
        throw new Error(`Failed to load area atlas data: ${response.status}`);
    }

    return response.json();
}

function buildAreaTokenChart(payload) {
    const topAreas = payload.area_summary_top;
    const host = document.getElementById("area-token-chart");
    if (!host || typeof echarts === "undefined") {
        return;
    }

    const chart = echarts.init(host);
    const colorStops = [
        "#7f0000",
        "#b30000",
        "#d95f0e",
        "#fe9929",
        "#fec44f",
        "#fff7bc"
    ];

    const option = {
        backgroundColor: "transparent",
        tooltip: {
            formatter(params) {
                const data = params.data;
                return [
                    `<strong>${data.name}</strong>`,
                    `Restaurants: ${data.value}`,
                    `Average Rating: ${data.rating.toFixed(2)}`
                ].join("<br>");
            }
        },
        series: [
            {
                type: "wordCloud",
                shape: "circle",
                left: "center",
                top: "center",
                width: "96%",
                height: "96%",
                right: null,
                bottom: null,
                sizeRange: [18, 62],
                rotationRange: [-25, 25],
                rotationStep: 5,
                gridSize: 8,
                drawOutOfBound: false,
                layoutAnimation: true,
                textStyle: {
                    fontFamily: "Segoe UI, sans-serif",
                    fontWeight: "700",
                    color(params) {
                        const index = params.dataIndex % colorStops.length;
                        return colorStops[index];
                    }
                },
                emphasis: {
                    textStyle: {
                        shadowBlur: 12,
                        shadowColor: "rgba(122, 31, 31, 0.35)"
                    }
                },
                data: topAreas.map((item) => ({
                    name: item.area,
                    value: item.restaurant_count,
                    rating: item.average_rating
                }))
            }
        ]
    };

    chart.setOption(option);
    window.addEventListener("resize", () => chart.resize());
}

function buildAreaViolinChart(payload) {
    const violinData = payload.violin_records;
    const traces = payload.area_summary_top.map((areaRecord) => {
        const areaRows = violinData.filter((item) => item.area === areaRecord.area);
        return {
            type: "box",
            name: areaRecord.area,
            x: areaRows.map((item) => item.rating),
            y: areaRows.map(() => areaRecord.area),
            orientation: "h",
            boxpoints: false,
            marker: {
                color: "#c44e52"
            },
            line: {
                color: "#7a1f1f",
                width: 1.2
            },
            fillcolor: "rgba(196, 78, 82, 0.42)"
        };
    });

    const layout = {
        margin: { l: 140, r: 16, t: 10, b: 48 },
        xaxis: {
            title: "Rating",
            gridcolor: "#ead7cf"
        },
        yaxis: {
            title: "Area",
            automargin: true,
            categoryorder: "array",
            categoryarray: payload.area_summary_top.map((item) => item.area).reverse()
        },
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot("area-violin-chart", traces, layout, { responsive: true });
}

function buildRatingBandChart(payload) {
    const areaOrder = payload.area_summary
        .slice(0, payload.meta.top_area_count)
        .map((item) => item.area);

    const bandColor = {
        fragile: "#8c2d04",
        developing: "#d95f0e",
        solid: "#fe9929",
        strong: "#fec44f",
        elite: "#fff7bc"
    };

    const traces = payload.rating_band_order.map((band) => {
        const bandMap = new Map(
            payload.rating_band_stack
                .filter((item) => item.rating_band === band)
                .map((item) => [item.area, item.restaurant_count])
        );

        return {
            type: "bar",
            name: band,
            x: areaOrder,
            y: areaOrder.map((area) => bandMap.get(area) || 0),
            marker: {
                color: bandColor[band] || "#cccccc"
            }
        };
    });

    const layout = {
        barmode: "stack",
        margin: { l: 52, r: 12, t: 12, b: 130 },
        xaxis: {
            title: "Area",
            tickangle: -55
        },
        yaxis: {
            title: "Restaurant Count",
            gridcolor: "#ead7cf"
        },
        legend: {
            orientation: "h",
            y: 1.15
        },
        annotations: payload.area_summary_top.map((item) => ({
            x: item.area,
            y: item.restaurant_count,
            text: String(item.restaurant_count),
            showarrow: false,
            yshift: -12,
            font: {
                size: 11,
                color: "#611818"
            }
        })),
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot("area-rating-band-chart", traces, layout, { responsive: true });
}

function buildAreaBubbleChart(payload) {
    const trace = {
        type: "scatter",
        mode: "markers",
        x: payload.area_summary.map((item) => item.restaurant_count),
        y: payload.area_summary.map((item) => item.average_rating),
        text: payload.area_summary.map((item) => item.area),
        textposition: "top center",
        marker: {
            size: payload.area_summary.map((item) => 10 + Math.sqrt(item.restaurant_count) * 2.2),
            color: payload.area_summary.map((item) => item.average_rating),
            cmin: 2.5,
            cmax: 4.5,
            colorscale: "Portland",
            opacity: 0.72,
            line: {
                color: "#6f1d1d",
                width: 0.7
            },
            colorbar: {
                title: "Average Rating"
            }
        },
        customdata: payload.area_summary.map((item) => [
            item.area,
            item.restaurant_count,
            item.average_rating
        ]),
        hovertemplate: [
            "<b>Area:</b> %{customdata[0]}<br>",
            "<b>Restaurants:</b> %{customdata[1]}<br>",
            "<b>Average Rating:</b> %{customdata[2]:.2f}<extra></extra>"
        ].join("")
    };

    const layout = {
        margin: { l: 56, r: 18, t: 12, b: 48 },
        xaxis: {
            title: "Restaurant Count",
            gridcolor: "#ead7cf"
        },
        yaxis: {
            title: "Average Rating",
            gridcolor: "#ead7cf"
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot("area-bubble-chart", [trace], layout, { responsive: true });
}

function buildAreaSupplyMap(payload) {
    const heatTrace = {
        type: "densitymapbox",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        z: payload.area_summary.map((item) => item.restaurant_count),
        radius: 34,
        colorscale: [
            [0.0, "#fff7ec"],
            [0.2, "#fee8c8"],
            [0.4, "#fdd49e"],
            [0.6, "#fdbb84"],
            [0.8, "#fc8d59"],
            [1.0, "#d7301f"]
        ],
        colorbar: { title: "Restaurant Count" },
        hoverinfo: "skip"
    };

    const hoverTrace = {
        type: "scattermapbox",
        mode: "markers",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        customdata: payload.area_summary.map((item) => [
            item.area,
            item.restaurant_count,
            item.average_rating
        ]),
        hovertemplate: [
            "<b>Area:</b> %{customdata[0]}<br>",
            "<b>Restaurants:</b> %{customdata[1]}<br>",
            "<b>Average Rating:</b> %{customdata[2]:.2f}<extra></extra>"
        ].join(""),
        marker: {
            size: 10,
            color: payload.area_summary.map((item) => item.restaurant_count),
            colorscale: "YlOrRd",
            opacity: 0.15,
            line: { color: "#742222", width: 0.4 },
            showscale: false
        }
    };

    const labelTrace = {
        type: "scattermapbox",
        mode: "text",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        text: payload.area_summary.map((item) => item.area),
        textfont: {
            size: 9,
            color: "#6a1f1f"
        },
        hoverinfo: "skip"
    };

    const layout = {
        mapbox: {
            style: "open-street-map",
            center: { lat: 13.01, lon: 80.20 },
            zoom: 9.3
        },
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot("area-supply-map", [heatTrace, hoverTrace, labelTrace], layout, { responsive: true });
}

function buildAreaRatingMap(payload) {
    const heatTrace = {
        type: "densitymapbox",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        z: payload.area_summary.map((item) => item.average_rating),
        radius: 30,
        zmin: 2.5,
        zmax: 4.5,
        colorscale: [
            [0.0, "#fff7fb"],
            [0.2, "#ece7f2"],
            [0.4, "#d0d1e6"],
            [0.6, "#a6bddb"],
            [0.8, "#74a9cf"],
            [1.0, "#0570b0"]
        ],
        colorbar: { title: "Average Rating" },
        hoverinfo: "skip"
    };

    const hoverTrace = {
        type: "scattermapbox",
        mode: "markers",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        customdata: payload.area_summary.map((item) => [
            item.area,
            item.restaurant_count,
            item.average_rating
        ]),
        hovertemplate: [
            "<b>Area:</b> %{customdata[0]}<br>",
            "<b>Restaurants:</b> %{customdata[1]}<br>",
            "<b>Average Rating:</b> %{customdata[2]:.2f}<extra></extra>"
        ].join(""),
        marker: {
            size: 9,
            color: payload.area_summary.map((item) => item.average_rating),
            cmin: 2.5,
            cmax: 4.5,
            colorscale: [
                [0.0, "#fff7fb"],
                [0.2, "#ece7f2"],
                [0.4, "#d0d1e6"],
                [0.6, "#a6bddb"],
                [0.8, "#74a9cf"],
                [1.0, "#0570b0"]
            ],
            opacity: 0.18,
            line: { color: "#1f4e79", width: 0.4 },
            showscale: false
        }
    };

    const labelTrace = {
        type: "scattermapbox",
        mode: "text",
        lat: payload.area_summary.map((item) => item.latitude),
        lon: payload.area_summary.map((item) => item.longitude),
        text: payload.area_summary.map((item) => item.area),
        textfont: {
            size: 9,
            color: "#154d77"
        },
        hoverinfo: "skip"
    };

    const layout = {
        mapbox: {
            style: "carto-positron",
            center: { lat: 13.01, lon: 80.20 },
            zoom: 9.3
        },
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot("area-rating-map", [heatTrace, hoverTrace, labelTrace], layout, { responsive: true });
}

function buildAreaQuadrantChart(payload) {
    const { median_count, median_rating, records } = payload.quadrant;

    const quadrantConfig = {
        "Mature & Quality":              { color: "#2f6b45", symbol: "circle" },
        "Hidden Gem / Potential":        { color: "#1e6f8c", symbol: "diamond" },
        "Competitive & Volatile":        { color: "#d89a24", symbol: "triangle-up" },
        "Underdeveloped":                { color: "#b85c38", symbol: "square" },
    };

    const grouped = {};
    records.forEach((r) => {
        if (!grouped[r.quadrant]) grouped[r.quadrant] = [];
        grouped[r.quadrant].push(r);
    });

    const traces = Object.keys(grouped).map((q) => {
        const items = grouped[q];
        const cfg = quadrantConfig[q] || { color: "#999", symbol: "circle" };
        return {
            type: "scatter",
            mode: "markers",
            name: q,
            x: items.map((d) => d.restaurant_count),
            y: items.map((d) => d.average_rating),
            text: items.map((d) => d.area),
            textposition: "top center",
            textfont: { size: 9, color: "#2b2522" },
            marker: {
                size: 12,
                color: cfg.color,
                symbol: cfg.symbol,
                opacity: 0.78,
                line: { color: "#fff", width: 1 },
            },
            customdata: items.map((d) => [d.area, d.restaurant_count, d.average_rating]),
            hovertemplate:
                "<b>%{customdata[0]}</b><br>" +
                "Restaurants: %{customdata[1]}<br>" +
                "Avg Rating: %{customdata[2]:.2f}<extra></extra>",
        };
    });

    const xRange = records.map((d) => d.restaurant_count);
    const yRange = records.map((d) => d.average_rating);
    const xMax = Math.max(...xRange) * 1.08;
    const yMin = Math.min(...yRange) - 0.1;
    const yMax = Math.max(...yRange) + 0.1;

    const shapes = [
        // vertical median line
        {
            type: "line",
            x0: median_count, x1: median_count,
            y0: yMin, y1: yMax,
            line: { color: "#999", width: 1, dash: "dash" },
        },
        // horizontal median line
        {
            type: "line",
            x0: 0, x1: xMax,
            y0: median_rating, y1: median_rating,
            line: { color: "#999", width: 1, dash: "dash" },
        },
    ];

    const annotations = [
        // quadrant labels
        {
            x: 0.98, y: 0.98, xref: "paper", yref: "paper",
            text: "<b>Mature &amp; Quality</b>",
            showarrow: false, font: { size: 11, color: "#2f6b45" },
            align: "right",
        },
        {
            x: 0.02, y: 0.98, xref: "paper", yref: "paper",
            text: "<b>Hidden Gem / Potential</b>",
            showarrow: false, font: { size: 11, color: "#1e6f8c" },
            align: "left",
        },
        {
            x: 0.98, y: 0.02, xref: "paper", yref: "paper",
            text: "<b>Competitive &amp; Volatile</b>",
            showarrow: false, font: { size: 11, color: "#d89a24" },
            align: "right",
        },
        {
            x: 0.02, y: 0.02, xref: "paper", yref: "paper",
            text: "<b>Underdeveloped</b>",
            showarrow: false, font: { size: 11, color: "#b85c38" },
            align: "left",
        },
    ];

    const layout = {
        margin: { l: 56, r: 18, t: 12, b: 48 },
        xaxis: {
            title: "Restaurant Count (Supply)",
            gridcolor: "#ead7cf",
            range: [0, xMax],
        },
        yaxis: {
            title: "Average Rating",
            gridcolor: "#ead7cf",
            range: [yMin, yMax],
        },
        shapes: shapes,
        annotations: annotations,
        legend: {
            orientation: "h",
            y: 1.12,
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot("area-quadrant-chart", traces, layout, { responsive: true });
}

async function renderAreaAtlasPage() {
    const chartHost = document.getElementById("area-token-chart");
    if (!chartHost) {
        return;
    }

    try {
        const payload = await loadAreaAtlasData();
        buildAreaTokenChart(payload);
        buildAreaViolinChart(payload);
        buildRatingBandChart(payload);
        buildAreaBubbleChart(payload);
        buildAreaSupplyMap(payload);
        buildAreaRatingMap(payload);
        buildAreaQuadrantChart(payload);
    } catch (error) {
        console.error(error);
        chartHost.innerHTML = "Failed to load area dashboard.";
    }
}

document.addEventListener("DOMContentLoaded", renderAreaAtlasPage);

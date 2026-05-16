async function loadOverviewData() {
    const response = await fetch("/api/overview");

    if (!response.ok) {
        throw new Error(`Failed to load overview data: ${response.status}`);
    }

    return response.json();
}

function spreadOverlappingRestaurants(restaurants) {
    const groupedRestaurants = new Map();

    restaurants.forEach((item) => {
        const key = `${Number(item.latitude).toFixed(4)}|${Number(item.longitude).toFixed(4)}`;
        if (!groupedRestaurants.has(key)) {
            groupedRestaurants.set(key, []);
        }
        groupedRestaurants.get(key).push(item);
    });

    const spreadRestaurants = [];
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));

    groupedRestaurants.forEach((group) => {
        if (group.length === 1) {
            spreadRestaurants.push({
                ...group[0],
                plot_latitude: Number(group[0].latitude),
                plot_longitude: Number(group[0].longitude)
            });
            return;
        }

        group.forEach((restaurant, index) => {
            const angle = index * goldenAngle;
            const radius = 0.00035 * Math.sqrt(index + 1);
            const latitudeOffset = radius * Math.cos(angle);
            const longitudeOffset = radius * Math.sin(angle);

            spreadRestaurants.push({
                ...restaurant,
                plot_latitude: Number(restaurant.latitude) + latitudeOffset,
                plot_longitude: Number(restaurant.longitude) + longitudeOffset
            });
        });
    });

    return spreadRestaurants;
}

function buildMapTrace(restaurants) {
    return {
        type: "scattermapbox",
        mode: "markers",
        lat: restaurants.map((item) => Number(item.plot_latitude)),
        lon: restaurants.map((item) => Number(item.plot_longitude)),
        text: restaurants.map((item) => String(item.restaurant_id)),
        textposition: "top center",
        textfont: {
            size: 8,
            color: "#4a1f1f"
        },
        customdata: restaurants.map((item) => [
            item.restaurant_id,
            item.restaurant,
            item.area,
            item.cuisine,
            item.rating
        ]),
        hovertemplate: [
            "<b>ID:</b> %{customdata[0]}<br>",
            "<b>Restaurant:</b> %{customdata[1]}<br>",
            "<b>Area:</b> %{customdata[2]}<br>",
            "<b>Cuisine:</b> %{customdata[3]}<br>",
            "<b>Rating:</b> %{customdata[4]}<extra></extra>"
        ].join(""),
        marker: {
            size: 9,
            opacity: 0.85,
            color: restaurants.map((item) => Number(item.rating)),
            cmin: 0,
            cmax: 5,
            colorscale: [
                [0.0, "#ffffff"],
                [0.2, "#ffe5e5"],
                [0.4, "#ffb3b3"],
                [0.6, "#ff8080"],
                [0.8, "#e64d4d"],
                [1.0, "#b30000"]
            ],
            colorbar: {
                title: "Rating"
            },
            line: {
                width: 0.5,
                color: "#7a1f1f"
            }
        }
    };
}

function buildMapLayout(restaurants) {
    const latitudes = restaurants.map((item) => Number(item.latitude));
    const longitudes = restaurants.map((item) => Number(item.longitude));

    const avgLatitude =
        latitudes.reduce((sum, value) => sum + value, 0) / latitudes.length;
    const avgLongitude =
        longitudes.reduce((sum, value) => sum + value, 0) / longitudes.length;

    return {
        title: {
            text: "Chennai Restaurant Map",
            x: 0.02
        },
        mapbox: {
            style: "open-street-map",
            center: {
                lat: avgLatitude,
                lon: avgLongitude
            },
            zoom: 9.8
        },
        margin: {
            l: 0,
            r: 0,
            t: 50,
            b: 0
        },
        paper_bgcolor: "#ffffff",
        plot_bgcolor: "#ffffff"
    };
}

function buildMapConfig() {
    return {
        responsive: true,
        displayModeBar: true
    };
}

async function renderOverviewMap() {
    const mapElement = document.getElementById("overview-map");

    if (!mapElement) {
        return;
    }


    try {
        const restaurants = await loadOverviewData();
        const spreadRestaurants = spreadOverlappingRestaurants(restaurants);

        if (spreadRestaurants.length === 0) {
            mapElement.innerHTML = "No valid restaurant coordinates found.";
            return;
        }

        const trace = buildMapTrace(spreadRestaurants);
        const layout = buildMapLayout(restaurants);
        const config = buildMapConfig();

        await Plotly.newPlot(mapElement, [trace], layout, config);
    } catch (error) {
        console.error(error);
        mapElement.innerHTML = "Failed to load overview map.";
    }
}

async function loadSegmentHistograms() {
    const resp = await fetch("/api/overview/segment-histograms");
    if (!resp.ok) throw new Error(`Failed to load segment histograms: ${resp.status}`);
    return resp.json();
}

async function loadAreaHistograms() {
    const resp = await fetch("/api/overview/area-histograms");
    if (!resp.ok) throw new Error(`Failed to load area histograms: ${resp.status}`);
    return resp.json();
}

function buildHistogramCard(gridElement, containerId, title, subtitle, binLabels, counts) {
    const card = document.createElement("div");
    card.className = "histogram-card";
    card.innerHTML = `
        <div class="histogram-card-header">
            <h3>${title}</h3>
            <p>${subtitle}</p>
        </div>
        <div id="${containerId}" class="chart-host-mini"></div>
    `;
    gridElement.appendChild(card);

    const trace = {
        type: "bar",
        x: binLabels,
        y: counts,
        marker: {
            color: counts.map((_, i) => {
                const ratio = i / Math.max(binLabels.length - 1, 1);
                const r = Math.round(180 + ratio * 36);
                const g = Math.round(80 - ratio * 40);
                const b = Math.round(50 - ratio * 20);
                return `rgba(${r}, ${g}, ${b}, 0.78)`;
            }),
            line: { color: "#7a1f1f", width: 0.6 },
        },
        hovertemplate: "<b>%{x}</b><br>Count: %{y}<extra></extra>",
    };

    const layout = {
        margin: { l: 40, r: 8, t: 4, b: 50 },
        xaxis: {
            tickangle: -45,
            tickfont: { size: 9 },
            gridcolor: "#ead7cf",
        },
        yaxis: {
            tickfont: { size: 9 },
            gridcolor: "#ead7cf",
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true });
}

async function renderSegmentHistograms() {
    const grid = document.getElementById("segment-histogram-grid");
    if (!grid) return;

    try {
        const payload = await loadSegmentHistograms();
        payload.group_order.forEach((name, idx) => {
            buildHistogramCard(
                grid,
                `segment-histogram-${idx}`,
                name,
                `n = ${payload.groups[name].reduce((a, b) => a + b, 0).toLocaleString()}`,
                payload.bin_labels,
                payload.groups[name]
            );
        });
    } catch (error) {
        console.error(error);
        grid.innerHTML = "Failed to load segment histograms.";
    }
}

async function renderAreaHistograms() {
    const grid = document.getElementById("area-histogram-grid");
    if (!grid) return;

    try {
        const payload = await loadAreaHistograms();
        payload.group_order.forEach((name, idx) => {
            buildHistogramCard(
                grid,
                `area-histogram-${idx}`,
                name,
                `n = ${payload.groups[name].reduce((a, b) => a + b, 0).toLocaleString()}`,
                payload.bin_labels,
                payload.groups[name]
            );
        });
    } catch (error) {
        console.error(error);
        grid.innerHTML = "Failed to load area histograms.";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    renderOverviewMap();
    renderSegmentHistograms();
    renderAreaHistograms();
});

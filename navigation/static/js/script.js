const modes = [
    { label: "Temperature Node", unit: "°C", windyOverlay: "temp" },
    { label: "Wind Velocity", unit: "km/h", windyOverlay: "wind" },
    { label: "Humidity Index", unit: "%", windyOverlay: "humidity" },
    { label: "Precipitation Index", unit: "mm", windyOverlay: "rain" }
];
let modeIdx = 0;

function cycleMode(dir) {
    modeIdx = (modeIdx + dir + modes.length) % modes.length;
    const m = modes[modeIdx];

    document.getElementById('data-label').innerText = m.label;
    document.getElementById('data-unit').innerText = m.unit;

    const iframe = document.getElementById('windy-frame');
    const currentUrl = new URL(iframe.src);
    currentUrl.searchParams.set('overlay', m.windyOverlay);
    iframe.src = currentUrl.toString();

    document.querySelectorAll('.bar').forEach(b => {
        b.style.height = (Math.random() * 60 + 25) + "%";
    });

    document.getElementById('data-value').innerText = Math.floor(Math.random() * 15 + 20);
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('state-search').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.toLowerCase().trim();
            const points = {
                'maharashtra': {lat: 19.75, lon: 75.71},
                'west bengal': {lat: 22.98, lon: 87.85},
                'delhi': {lat: 28.61, lon: 77.20},
                'sikkim': {lat: 27.53, lon: 88.51},
                'kerala': {lat: 10.85, lon: 76.27}
            };
            if (points[query]) {
                const p = points[query];
                const iframe = document.getElementById('windy-frame');
                const url = new URL(iframe.src);
                url.searchParams.set('lat', p.lat);
                url.searchParams.set('lon', p.lon);
                url.searchParams.set('zoom', '7');
                iframe.src = url.toString();
                document.getElementById('data-coords').innerText = `Focused: ${query.toUpperCase()}`;
            }
        }
    });

    const clock = document.getElementById('clock');
    if (clock) {
        setInterval(() => {
            const now = new Date();
            const hh = String(now.getHours()).padStart(2, '0');
            const mm = String(now.getMinutes()).padStart(2, '0');
            const ss = String(now.getSeconds()).padStart(2, '0');
            clock.innerText = `${hh}:${mm}:${ss}`;
        }, 1000);
    }
});

const socket = io();
let chart;

function submitForm() {
    const data = {
        username: username.value,
        email: email.value,
        mode: mode.value,
        type: type.value,
        decision: decision.value
    };

    fetch("/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: username.value,
            email: email.value,
            mode: mode.value,
            type: type.value,
            decision: decision.value
        })
    })
    .then(res => res.json())
    .then(res => {
        msg.innerText = res.error || "Submitted successfully!";
    });

}

function updateChart(data) {
    const labels = [
        "Accepted",
        "Rejected",
        "Not Able to Pick",
        "Not Able to Access Mail"
    ];

    const prime = labels.map(l => data["Prime/Digital"]?.[l] || 0);
    const ninja = labels.map(l => data["Ninja"]?.[l] || 0);

    if (chart) chart.destroy();

    chart = new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                { label: "Prime/Digital", data: prime },
                { label: "Ninja", data: ninja }
            ]
        }
    });
}

function refresh() {
    fetch("/stats")
        .then(r => r.json())
        .then(updateChart);
}

function updateCounts() {
    fetch("/live-counts")
        .then(r => r.json())
        .then(data => {
            document.getElementById("acceptedCount").innerText = data["Accepted"] || 0;
            document.getElementById("rejectedCount").innerText = data["Rejected"] || 0;
            document.getElementById("pickCount").innerText = data["Not Able to Pick"] || 0;
            document.getElementById("mailCount").innerText = data["Not Able to Access Mail"] || 0;
        });
}

// 🔴 LIVE update when any user submits
socket.on("update", () => {
    refresh();       // chart
    updateCounts();  // counts
});

// Initial load
updateCounts();


socket.on("update", refresh);
refresh();


function updateRadiationChart(cpm) {
    const ctx = document.getElementById('radiationChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Current Radiation'],
            datasets: [{
                label: 'CPM',
                data: [cpm],
                backgroundColor: cpm < 30 ? 'green' : cpm < 80 ? 'orange' : 'red',
                borderWidth: 1
            }]
        },
        options: {
            scales: { y: { beginAtZero: true, max: 100 } },
            plugins: { legend: { display: false } }
        }
    });
}

function updateHistoryChart(cpmData, labels) {
    const ctx = document.getElementById('historyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'CPM Over Time',
                data: cpmData,
                borderColor: 'blue',
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: true } }
        }
    });
}

function updateTrendChart(cpmData, labels) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Radiation Trend',
                data: cpmData,
                borderColor: 'purple',
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: true } }
        }
    });
}
// Función global para crear o actualizar gráficos de línea
function createOrUpdateLineChart(chartId, cpmData, labels, titleText, yAxisLabel, color = 'rgba(75, 192, 192, 1)') {
    const ctx = document.getElementById(chartId);
    if (!ctx) {
        console.error(`Canvas element with ID '${chartId}' not found.`);
        return;
    }

    // Destruir la instancia de gráfico anterior si existe
    if (window[chartId + 'ChartInstance']) {
        window[chartId + 'ChartInstance'].destroy();
    }

    window[chartId + 'ChartInstance'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'CPM (Counts Per Minute)',
                data: cpmData,
                borderColor: color,
                backgroundColor: color.replace('1)', '0.2)'), // Versión transparente para el relleno
                borderWidth: 2,
                tension: 0.3, // Suaviza la línea del gráfico
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Permite que el gráfico ajuste su tamaño
            plugins: {
                title: {
                    display: true,
                    text: titleText,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `CPM: ${context.raw}`;
                        },
                        title: function(context) {
                            return `Tiempo: ${context.label}`;
                        }
                    }
                },
                legend: {
                    display: false // No mostrar la leyenda si solo hay un dataset
                }
            },
            scales: {
                x: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
                    }
                }
            }
        }
    });
}

// Puedes añadir más funciones para otros tipos de gráficos si los necesitas
// Por ejemplo, para un gráfico de barras o de pastel

// Función global para crear o actualizar gráficos de línea
function createOrUpdateLineChart(chartId, cpmData, labels, titleText, yAxisLabel, color = 'rgba(75, 192, 192, 1)') {
    const ctx = document.getElementById(chartId);
    if (!ctx) {
        console.error(`Canvas element with ID '${chartId}' not found.`);
        return;
    }

    // Destruir la instancia de gráfico anterior si existe
    if (window[chartId + 'ChartInstance']) {
        window[chartId + 'ChartInstance'].destroy();
    }

    window[chartId + 'ChartInstance'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'CPM (Counts Per Minute)',
                data: cpmData,
                borderColor: color,
                backgroundColor: color.replace('1)', '0.2)'), // Versión transparente para el relleno
                borderWidth: 2,
                tension: 0.3, // Suaviza la línea del gráfico
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Permite que el gráfico ajuste su tamaño
            plugins: {
                title: {
                    display: true,
                    text: titleText,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `CPM: ${context.raw}`;
                        },
                        title: function(context) {
                            return `Tiempo: ${context.label}`;
                        }
                    }
                },
                legend: {
                    display: false // No mostrar la leyenda si solo hay un dataset
                }
            },
            scales: {
                x: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
                    }
                }
            }
        }
    });
}

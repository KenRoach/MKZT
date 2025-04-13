// Chart configurations
const chartConfigs = {
    requestChart: {
        type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    },
    errorChart: {
        type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    },
    memoryChart: {
        type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Memory Usage (MB)'
                    }
                }
            }
        }
    },
    cpuChart: {
        type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'CPU Usage (%)'
                    }
                }
            }
        }
    },
    requestTypesChart: {
        type: 'doughnut',
        options: {
            responsive: true
        }
    }
};

// Initialize charts
const charts = {};
Object.keys(chartConfigs).forEach(chartId => {
    const ctx = document.getElementById(chartId).getContext('2d');
    charts[chartId] = new Chart(ctx, {
        type: chartConfigs[chartId].type,
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#4C51BF',
                    '#48BB78',
                    '#ED8936',
                    '#ED64A6'
                ]
            }]
        },
        options: chartConfigs[chartId].options
    });
});

// Update health status
function updateHealthStatus(health) {
    const healthStatus = document.getElementById('healthStatus');
    healthStatus.innerHTML = '';

    Object.entries(health.checks).forEach(([check, data]) => {
        const statusColor = data.status === 'healthy' ? 'bg-green-100' : 
                          data.status === 'warning' ? 'bg-yellow-100' : 'bg-red-100';
        const textColor = data.status === 'healthy' ? 'text-green-800' : 
                         data.status === 'warning' ? 'text-yellow-800' : 'text-red-800';

        const card = document.createElement('div');
        card.className = `p-4 rounded-lg ${statusColor}`;
        card.innerHTML = `
            <h3 class="font-semibold ${textColor}">${check}</h3>
            <p class="text-sm ${textColor}">Status: ${data.status}</p>
            <p class="text-sm ${textColor}">Value: ${data.value}</p>
            <p class="text-sm ${textColor}">Threshold: ${data.threshold}</p>
            <p class="text-sm ${textColor}">Severity: ${data.severity}</p>
            <p class="text-sm ${textColor}">${data.description}</p>
        `;
        healthStatus.appendChild(card);
    });
}

// Update metrics charts
function updateMetricsCharts(metrics) {
    // Update request chart
    charts.requestChart.data.labels = ['Total Requests'];
    charts.requestChart.data.datasets[0].data = [metrics.total_requests];
    charts.requestChart.update();

    // Update error chart
    charts.errorChart.data.labels = ['Error Rate'];
    charts.errorChart.data.datasets[0].data = [metrics.error_rate];
    charts.errorChart.update();

    // Update memory chart
    charts.memoryChart.data.labels = ['Memory Usage'];
    charts.memoryChart.data.datasets[0].data = [metrics.system_metrics.current_memory_usage_mb];
    charts.memoryChart.update();

    // Update CPU chart
    charts.cpuChart.data.labels = ['CPU Usage'];
    charts.cpuChart.data.datasets[0].data = [metrics.system_metrics.current_cpu_usage_percent];
    charts.cpuChart.update();

    // Update request types chart
    const requestTypes = metrics.request_types;
    charts.requestTypesChart.data.labels = Object.keys(requestTypes);
    charts.requestTypesChart.data.datasets[0].data = Object.values(requestTypes);
    charts.requestTypesChart.update();
}

// Fetch and update data
async function updateDashboard() {
    try {
        // Fetch current metrics
        const metricsResponse = await fetch('/api/metrics');
        const metrics = await metricsResponse.json();
        updateMetricsCharts(metrics);

        // Fetch health status
        const healthResponse = await fetch('/api/health');
        const health = await healthResponse.json();
        updateHealthStatus(health);

    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Update dashboard every 5 seconds
setInterval(updateDashboard, 5000);
updateDashboard(); // Initial update 
document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("desempenhoAreaChart");
    if (!canvas || typeof Chart === "undefined") return;

    const labels = JSON.parse(document.getElementById("labels-area-data").textContent);
    const values = JSON.parse(document.getElementById("dados-area-data").textContent);

    new Chart(canvas, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Desempenho (%)",
                    data: values,
                    backgroundColor: "rgba(91, 78, 230, 0.20)",
                    borderColor: "#5b4ee6",
                    pointBackgroundColor: "#5b4ee6",
                    pointBorderColor: "#ffffff",
                    pointHoverBackgroundColor: "#ffffff",
                    pointHoverBorderColor: "#5b4ee6",
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            scale: {
                ticks: {
                    beginAtZero: true,
                    min: 0,
                    max: 100,
                    stepSize: 20
                }
            }
        }
    });
});
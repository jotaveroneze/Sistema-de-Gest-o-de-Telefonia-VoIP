document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("/grafico-telefones");
    const dados = await response.json();

    const labels = dados.map(item => item.secretaria);
    const montados = dados.map(item => item.montados);
    const naoMontados = dados.map(item => item.nao_montados);

    const ctx = document.getElementById("graficoTelefones");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Entregues",
                    data: montados,
                    stack: "telefones",
                    backgroundColor: "#0d6efd",
                    borderRadius: 6,
                    barThickness: 28
                },
                {
                    label: "Não entregue",
                    data: naoMontados,
                    stack: "telefones",
                    backgroundColor: "#dc3545",
                    borderRadius: 6,
                    barThickness: 28
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: "easeOutQuart"
            },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        usePointStyle: true,
                        pointStyle: "rectRounded",
                        padding: 20,
                        font: {
                            size: 13,
                            family: "Arial"
                        }
                    }
                },
                title: {
                    display: true,
                    text: "Telefones por Secretaria",
                    padding: {
                        top: 10,
                        bottom: 20
                    },
                    font: {
                        size: 16,
                        weight: "600"
                    },
                    color: "#2B2F33"
                },
                tooltip: {
                    backgroundColor: "#1f2937",
                    padding: 12,
                    titleFont: { size: 13 },
                    bodyFont: { size: 13 },
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: "#6c757d",
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: "#eef0f2"
                    },
                    ticks: {
                        color: "#6c757d",
                        stepSize: 1
                    }
                }
            }
        }
    });
});

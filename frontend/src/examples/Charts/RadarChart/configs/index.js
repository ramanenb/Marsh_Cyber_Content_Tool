function configs(labels, datasets) {
  return {
    data: {
      labels,
      datasets: datasets.map((ds) => ({
        ...ds,
        fill: true,
        backgroundColor: ds.backgroundColor || "rgba(255, 99, 132, 0.2)", // soft blue fill
        borderColor: ds.borderColor || "#003366",
        pointBackgroundColor: ds.pointBackgroundColor || "rgba(196, 42, 42, 1)"
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
          position: "top",
          labels: {
            color: "#333",
          },
        },
      },
      scales: {
        r: {
          angleLines: {
            color: "#e0e0e0",
          },
          grid: {
            color: "#e0e0e0",
          },
          pointLabels: {
            color: "#333",
            font: { size: 12 },
            display: false
          },
          ticks: {
            backdropColor: "#fff", // makes hexagon appear white
            color: "#555",
            showLabelBackdrop: false,
          },
        },
      },
    },
  };
}

export default configs;

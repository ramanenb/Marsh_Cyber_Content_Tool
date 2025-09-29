import typography from "assets/theme/base/typography";

function configs(labels, datasets) {
  return {
    data: {
      labels,
      datasets: [...datasets],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            // Show full label in tooltip
            title: function (context) {
              return context[0].label;
            },
          },
        },
      },
      scales: {
        y: {
          grid: {
            drawBorder: false,
            display: true,
            drawOnChartArea: true,
            drawTicks: false,
            borderDash: [5, 5],
            color: "#c1c4ce5c",
          },
          ticks: {
            display: true,
            color: "#b2b9bf",
            padding: 12,
            font: {
              size: 11,
              family: typography.fontFamily,
              style: "normal",
              lineHeight: 2,
            },
            // Truncate y-axis labels to 13 chars
            callback: function (value) {
              const label = this.getLabelForValue(value);
              return label.length > 13 ? label.slice(0, 13) + "…" : label;
            },
          },
        },
        x: {
          grid: {
            drawBorder: false,
            display: false,
            drawOnChartArea: false,
            drawTicks: true,
            color: "#c1c4ce5c",
          },
          ticks: {
            display: true,
            color: "#b2b9bf",
            padding: 12,
          },
        },
      },
    },
  };
}

export default configs;

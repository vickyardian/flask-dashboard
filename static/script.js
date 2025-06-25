let currentSelectedPTN = null;

function selectPTN(ptnName) {
  // Update UI
  document.querySelectorAll(".ptn-card").forEach((card) => {
    card.classList.remove("active");
  });
  document.querySelector(`[data-ptn="${ptnName}"]`).classList.add("active");
  document.getElementById(
    "selected-ptn-display"
  ).textContent = `PTN Terpilih: ${ptnName}`;

  // Show sections & loader, hide old charts & stats
  const interactiveSection = document.getElementById("interactive-section");
  interactiveSection.style.display = "block";
  document.getElementById("loading").style.display = "block";
  document.getElementById("charts-container").style.display = "none";
  document.getElementById("ptn-stats-summary").style.display = "none"; // Sembunyikan statistik lama

  currentSelectedPTN = ptnName;

  // Smooth scroll
  interactiveSection.scrollIntoView({ behavior: "smooth", block: "start" });

  // Fetch data
  fetch(`/api/charts/${encodeURIComponent(ptnName)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // ========== PERBARUI BLOK STATISTIK RATA-RATA ==========
        document.getElementById("avg-daya-tampung").textContent =
          data.avg_daya_tampung || "N/A";
        document.getElementById("avg-ukt").textContent = data.avg_ukt || "N/A";
        document.getElementById("ptn-stats-summary").style.display = "grid"; // Tampilkan statistik
        // ========================================================

        renderCharts(data);
        updateTable(data.table_data);
        showChartsContainer();
      } else {
        handleError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      handleError("Gagal memuat data");
    });
}

function renderCharts(data) {
  // Pie chart
  const pieData = JSON.parse(data.pie_chart);
  Plotly.newPlot(
    "pie-chart",
    pieData.data,
    {
      ...pieData.layout,
      autosize: true,
      margin: { l: 50, r: 50, t: 50, b: 50 },
    },
    { responsive: true, displayModeBar: false }
  );

  // Bar chart
  const barData = JSON.parse(data.bar_chart);
  Plotly.newPlot(
    "bar-chart",
    barData.data,
    {
      ...barData.layout,
      autosize: true,
      margin: { l: 200, r: 50, t: 50, b: 50 }, // Increased left margin
    },
    { responsive: true, displayModeBar: false }
  );
}

function updateTable(tableData) {
  const tableBody = document.getElementById("table-body");
  tableBody.innerHTML = "";
  tableData.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${row.JURUSAN}</td>
            <td>${row["DAYA TAMPUNG"] || "N/A"}</td>
            <td>${row.UKT}</td>
        `;
    tableBody.appendChild(tr);
  });
}

function showChartsContainer() {
  document.getElementById("loading").style.display = "none";
  document.getElementById("charts-container").style.display = "flex"; // Diubah ke flex

  // Resize charts
  setTimeout(() => {
    Plotly.Plots.resize(document.getElementById("pie-chart"));
    Plotly.Plots.resize(document.getElementById("bar-chart"));
  }, 100);
}

function handleError(message) {
  document.getElementById("loading").style.display = "none";
  document.getElementById("ptn-stats-summary").style.display = "none";
  alert("Terjadi kesalahan: " + (message || "Tidak ada data"));
}

// Responsive charts on window resize
window.addEventListener("resize", () => {
  if (currentSelectedPTN) {
    setTimeout(() => {
      Plotly.Plots.resize(document.getElementById("pie-chart"));
      Plotly.Plots.resize(document.getElementById("bar-chart"));
    }, 100);
  }
});

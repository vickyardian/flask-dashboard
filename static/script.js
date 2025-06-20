// Global variable to track current selected PTN
let currentSelectedPTN = null;

/**
 * Main function to handle PTN selection
 * @param {string} ptnName - Name of the selected PTN
 */
function selectPTN(ptnName) {
  // Remove active class from all cards
  document.querySelectorAll(".ptn-card").forEach((card) => {
    card.classList.remove("active");
  });

  // Add active class to selected card
  document.querySelector(`[data-ptn="${ptnName}"]`).classList.add("active");

  // Update selected PTN display
  document.getElementById(
    "selected-ptn-display"
  ).textContent = `PTN Terpilih: ${ptnName}`;

  // Show the interactive section
  document.getElementById("interactive-section").style.display = "block";

  // Show loading animation
  document.getElementById("loading").style.display = "block";
  document.getElementById("charts-container").style.display = "none";

  // Store current selected PTN
  currentSelectedPTN = ptnName;

  // Fetch data from API
  fetchPTNData(ptnName);
}

/**
 * Fetch PTN data from API and render charts
 * @param {string} ptnName - Name of the PTN to fetch data for
 */
function fetchPTNData(ptnName) {
  fetch(`/api/charts/${encodeURIComponent(ptnName)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        renderCharts(data);
        updateTable(data.table_data);
        showChartsContainer();
        scrollToInteractiveSection();
      } else {
        handleError("Error: " + data.error);
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      handleError("Terjadi kesalahan saat memuat data");
    });
}

/**
 * Render pie and bar charts
 * @param {Object} data - API response data containing chart data
 */
function renderCharts(data) {
  // Render pie chart
  const pieData = JSON.parse(data.pie_chart);
  const pieLayout = {
    ...pieData.layout,
    autosize: true,
    margin: { l: 50, r: 50, t: 50, b: 50 },
    showlegend: true,
    legend: {
      orientation: "v",
      x: 1.02,
      y: 0.5,
      xanchor: "left",
    },
  };

  const pieConfig = {
    responsive: true,
    displayModeBar: false,
  };

  Plotly.newPlot("pie-chart", pieData.data, pieLayout, pieConfig);

  // Render bar chart
  const barData = JSON.parse(data.bar_chart);
  const barLayout = {
    ...barData.layout,
    autosize: true,
    margin: { l: 100, r: 50, t: 50, b: 100 },
    showlegend: false,
  };

  const barConfig = {
    responsive: true,
    displayModeBar: false,
  };

  Plotly.newPlot("bar-chart", barData.data, barLayout, barConfig);
}

/**
 * Update the data table with PTN information
 * @param {Array} tableData - Array of table row data
 */
function updateTable(tableData) {
  const tableBody = document.getElementById("table-body");
  tableBody.innerHTML = "";

  tableData.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${row.JURUSAN}</td>
            <td>${row["DAYA TAMPUNG"] || "N/A"}</td>
            <td>${row.UKT_RUPIAH}</td>
        `;
    tableBody.appendChild(tr);
  });
}

/**
 * Show charts container and resize charts
 */
function showChartsContainer() {
  document.getElementById("loading").style.display = "none";
  document.getElementById("charts-container").style.display = "flex";

  // Force resize after a short delay to ensure proper rendering
  setTimeout(() => {
    Plotly.Plots.resize("pie-chart");
    Plotly.Plots.resize("bar-chart");
  }, 100);
}

/**
 * Smooth scroll to interactive section
 */
function scrollToInteractiveSection() {
  document.getElementById("interactive-section").scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

/**
 * Handle errors during data fetching
 * @param {string} message - Error message to display
 */
function handleError(message) {
  document.getElementById("loading").style.display = "none";
  alert("Terjadi kesalahan saat memuat data: " + message);
}

/**
 * Resize charts when window is resized
 */
function handleWindowResize() {
  if (currentSelectedPTN) {
    setTimeout(() => {
      Plotly.Plots.resize("pie-chart");
      Plotly.Plots.resize("bar-chart");
    }, 100);
  }
}

/**
 * Initialize event listeners and observers
 */
function initializeEventListeners() {
  // Handle window resize for responsive charts
  window.addEventListener("resize", handleWindowResize);

  // Ensure charts are properly sized when becoming visible
  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (
        mutation.type === "attributes" &&
        mutation.attributeName === "style"
      ) {
        const target = mutation.target;
        if (
          target.id === "charts-container" &&
          target.style.display === "flex"
        ) {
          setTimeout(() => {
            Plotly.Plots.resize("pie-chart");
            Plotly.Plots.resize("bar-chart");
          }, 200);
        }
      }
    });
  });

  observer.observe(document.getElementById("charts-container"), {
    attributes: true,
    attributeFilter: ["style"],
  });
}

/**
 * Make all Plotly charts responsive on page load
 */
function makeChartsResponsive() {
  setTimeout(() => {
    const plotlyDivs = document.querySelectorAll(".plotly-graph-div");
    plotlyDivs.forEach((div) => {
      if (div.layout) {
        Plotly.Plots.resize(div);
      }
    });
  }, 1000);
}

// Initialize everything when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initializeEventListeners();
  makeChartsResponsive();
});

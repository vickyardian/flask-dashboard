// ===== VARIABEL GLOBAL =====
// Menyimpan PTN yang sedang dipilih oleh pengguna
let currentSelectedPTN = null;

/**
 * Fungsi utama untuk memilih PTN dan menampilkan data terkait
 * @param {string} ptnName - Nama PTN yang dipilih
 */
function selectPTN(ptnName) {
  // Menghapus kelas 'active' dari semua kartu PTN
  document.querySelectorAll(".ptn-card").forEach((card) => {
    card.classList.remove("active");
  });

  // Menambahkan kelas 'active' pada kartu PTN yang dipilih
  document.querySelector(`[data-ptn="${ptnName}"]`).classList.add("active");

  // Menampilkan nama PTN yang dipilih
  document.getElementById(
    "selected-ptn-display"
  ).textContent = `PTN Terpilih: ${ptnName}`;

  // Menampilkan section interaktif dan loading, menyembunyikan chart lama
  const interactiveSection = document.getElementById("interactive-section");
  interactiveSection.style.display = "block"; // Tampilkan section interaktif
  document.getElementById("loading").style.display = "block"; // Tampilkan loading
  document.getElementById("charts-container").style.display = "none"; // Sembunyikan container chart
  document.getElementById("ptn-stats-summary").style.display = "none"; // Sembunyikan statistik

  // Menyimpan PTN yang dipilih ke variabel global
  currentSelectedPTN = ptnName;

  // Scroll otomatis ke section interaktif dengan animasi smooth
  interactiveSection.scrollIntoView({ behavior: "smooth", block: "start" });

  // Mengambil data dari server melalui API
  fetch(`/api/charts/${encodeURIComponent(ptnName)}`)
    .then((response) => response.json()) // Mengubah response menjadi JSON
    .then((data) => {
      // Jika data berhasil diambil
      if (data.success) {
        // ===== MEMPERBARUI STATISTIK RATA-RATA =====
        // Menampilkan rata-rata daya tampung
        document.getElementById("avg-daya-tampung").textContent =
          data.avg_daya_tampung || "N/A";
        // Menampilkan rata-rata UKT
        document.getElementById("avg-ukt").textContent = data.avg_ukt || "N/A";
        // Menampilkan blok statistik rata-rata
        document.getElementById("ptn-stats-summary").style.display = "grid";

        // Merender chart dan tabel dengan data yang diterima
        renderCharts(data);
        updateTable(data.table_data);
        showChartsContainer();
      } else {
        // Jika terjadi error dari server
        handleError(data.error);
      }
    })
    .catch((error) => {
      // Jika terjadi error dalam proses fetch
      console.error("Error:", error);
      handleError("Gagal memuat data");
    });
}

/**
 * Fungsi untuk merender chart menggunakan Plotly
 * @param {Object} data - Data yang berisi informasi chart
 */
function renderCharts(data) {
  // ===== MEMBUAT PIE CHART =====
  const pieData = JSON.parse(data.pie_chart); // Parse data JSON untuk pie chart
  Plotly.newPlot(
    "pie-chart", // ID element untuk pie chart
    pieData.data, // Data chart
    {
      ...pieData.layout, // Layout dari data
      autosize: true, // Chart menyesuaikan ukuran container
      margin: { l: 50, r: 50, t: 50, b: 50 }, // Margin chart
    },
    {
      responsive: true, // Chart responsif
      displayModeBar: false, // Sembunyikan toolbar Plotly
    }
  );

  // ===== MEMBUAT BAR CHART =====
  const barData = JSON.parse(data.bar_chart); // Parse data JSON untuk bar chart
  Plotly.newPlot(
    "bar-chart", // ID element untuk bar chart
    barData.data, // Data chart
    {
      ...barData.layout, // Layout dari data
      autosize: true, // Chart menyesuaikan ukuran container
      margin: { l: 200, r: 50, t: 50, b: 50 }, // Margin kiri diperbesar untuk label panjang
    },
    {
      responsive: true, // Chart responsif
      displayModeBar: false, // Sembunyikan toolbar Plotly
    }
  );
}

/**
 * Fungsi untuk memperbarui tabel dengan data baru
 * @param {Array} tableData - Array berisi data untuk tabel
 */
function updateTable(tableData) {
  const tableBody = document.getElementById("table-body"); // Ambil element tbody
  tableBody.innerHTML = ""; // Kosongkan isi tabel

  // Loop untuk setiap baris data
  tableData.forEach((row) => {
    const tr = document.createElement("tr"); // Buat element baris baru
    // Isi baris dengan data jurusan, daya tampung, dan UKT
    tr.innerHTML = `
            <td>${row.JURUSAN}</td>
            <td>${row["DAYA TAMPUNG"] || "N/A"}</td>
            <td>${row.UKT}</td>
        `;
    tableBody.appendChild(tr); // Tambahkan baris ke tabel
  });
}

/**
 * Fungsi untuk menampilkan container chart dan menyembunyikan loading
 */
function showChartsContainer() {
  document.getElementById("loading").style.display = "none"; // Sembunyikan loading
  document.getElementById("charts-container").style.display = "flex"; // Tampilkan container chart

  // Resize chart setelah container ditampilkan (dengan delay kecil)
  setTimeout(() => {
    Plotly.Plots.resize(document.getElementById("pie-chart")); // Resize pie chart
    Plotly.Plots.resize(document.getElementById("bar-chart")); // Resize bar chart
  }, 100);
}

/**
 * Fungsi untuk menangani error
 * @param {string} message - Pesan error yang akan ditampilkan
 */
function handleError(message) {
  document.getElementById("loading").style.display = "none"; // Sembunyikan loading
  document.getElementById("ptn-stats-summary").style.display = "none"; // Sembunyikan statistik
  alert("Terjadi kesalahan: " + (message || "Tidak ada data")); // Tampilkan alert error
}

// ===== EVENT LISTENER =====
// Event listener untuk resize window agar chart tetap responsif
window.addEventListener("resize", () => {
  // Jika ada PTN yang sedang dipilih
  if (currentSelectedPTN) {
    // Resize chart dengan delay kecil
    setTimeout(() => {
      Plotly.Plots.resize(document.getElementById("pie-chart")); // Resize pie chart
      Plotly.Plots.resize(document.getElementById("bar-chart")); // Resize bar chart
    }, 100);
  }
});

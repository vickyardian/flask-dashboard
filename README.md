# Dashboard Program IUP PTN Indonesia

Sebuah aplikasi web interaktif yang dibuat dengan Flask untuk menganalisis dan memvisualisasikan data Program Sarjana Internasional (International Undergraduate Program - IUP) di berbagai Perguruan Tinggi Negeri (PTN) di Indonesia. Dashboard ini menyajikan informasi mengenai jurusan, daya tampung, dan Uang Kuliah Tunggal (UKT).

## Fitur Utama

- **Statistik Ringkas**: Menampilkan jumlah total PTN, provinsi, kota, dan program studi yang terdaftar dalam dataset.
- **Visualisasi Data Agregat**:
  - Grafik program studi paling populer (paling banyak ditawarkan di berbagai PTN).
  - Grafik program studi dengan UKT tertinggi.
  - Grafik program studi dengan daya tampung terbesar.
  - Grafik distribusi jumlah PTN per provinsi.
- **Tampilan Detail per PTN**:
  - Pengguna dapat memilih PTN untuk melihat analisis yang lebih mendalam.
  - Menampilkan rata-rata daya tampung dan rata-rata UKT untuk PTN yang dipilih.
  - **Grafik Pie**: Distribusi daya tampung untuk setiap jurusan di PTN tersebut.
  - **Grafik Batang**: Perbandingan UKT antar jurusan di PTN tersebut.
  - **Tabel Rinci**: Menampilkan daftar program studi, daya tampung, dan besaran UKT dalam format tabel.

## Sumber Data

Data yang digunakan dalam proyek ini berasal dari file `MINI_TIM_B.csv`, yang berisi kompilasi data dari berbagai sumber mengenai program IUP di Indonesia.

## Teknologi yang Digunakan

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Library Python**:
    - Pandas & Numpy untuk manipulasi data
    - Plotly untuk pembuatan grafik interaktif
- **Server**: Gunicorn (untuk deployment)

## Cara Menjalankan Proyek Secara Lokal

1.  **Clone repository ini:**
    ```bash
    git clone [https://github.com/vickyardian/flask-dashboard.git](https://github.com/vickyardian/flask-dashboard.git)
    cd flask-dashboard
    ```

2.  **(Opsional) Buat dan aktifkan virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install semua dependensi yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan aplikasi Flask:**
    ```bash
    python app.py
    ```

5.  Buka browser Anda dan kunjungi `http://127.0.0.1:5000`.

## Struktur Proyek
Tentu, saya akan sediakan konten lengkapnya agar Anda bisa langsung menyalin dan menyimpannya sebagai file README.md.

Cara membuat file:

Salin semua teks yang ada di dalam kotak di bawah ini.

Buat file baru di dalam proyek Anda dengan nama README.md.

Tempel (paste) teks yang sudah Anda salin ke dalam file tersebut.

Simpan file tersebut.

Markdown

# Dashboard Program IUP PTN Indonesia

Sebuah aplikasi web interaktif yang dibuat dengan Flask untuk menganalisis dan memvisualisasikan data Program Sarjana Internasional (International Undergraduate Program - IUP) di berbagai Perguruan Tinggi Negeri (PTN) di Indonesia. Dashboard ini menyajikan informasi mengenai jurusan, daya tampung, dan Uang Kuliah Tunggal (UKT).

## Fitur Utama

- **Statistik Ringkas**: Menampilkan jumlah total PTN, provinsi, kota, dan program studi yang terdaftar dalam dataset.
- **Visualisasi Data Agregat**:
  - Grafik program studi paling populer (paling banyak ditawarkan di berbagai PTN).
  - Grafik program studi dengan UKT tertinggi.
  - Grafik program studi dengan daya tampung terbesar.
  - Grafik distribusi jumlah PTN per provinsi.
- **Tampilan Detail per PTN**:
  - Pengguna dapat memilih PTN untuk melihat analisis yang lebih mendalam.
  - Menampilkan rata-rata daya tampung dan rata-rata UKT untuk PTN yang dipilih.
  - **Grafik Pie**: Distribusi daya tampung untuk setiap jurusan di PTN tersebut.
  - **Grafik Batang**: Perbandingan UKT antar jurusan di PTN tersebut.
  - **Tabel Rinci**: Menampilkan daftar program studi, daya tampung, dan besaran UKT dalam format tabel.

## Sumber Data

Data yang digunakan dalam proyek ini berasal dari file `MINI_TIM_B.csv`, yang berisi kompilasi data dari berbagai sumber mengenai program IUP di Indonesia.

## Teknologi yang Digunakan

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Library Python**:
    - Pandas & Numpy untuk manipulasi data
    - Plotly untuk pembuatan grafik interaktif
- **Server**: Gunicorn (untuk deployment)

## Cara Menjalankan Proyek Secara Lokal

1.  **Clone repository ini:**
    ```bash
    git clone [https://github.com/vickyardian/flask-dashboard.git](https://github.com/vickyardian/flask-dashboard.git)
    cd flask-dashboard
    ```

2.  **(Opsional) Buat dan aktifkan virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install semua dependensi yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan aplikasi Flask:**
    ```bash
    python app.py
    ```

5.  Buka browser Anda dan kunjungi `http://127.0.0.1:5000`.

## Struktur Proyek

/
|-- app.py                  # File utama aplikasi Flask
|-- MINI_TIM_B.csv          # Dataset utama
|-- requirements.txt        # Daftar dependensi Python
|-- .render.yaml            # Konfigurasi deployment untuk Render
|-- .gitignore              # File dan folder yang diabaikan oleh Git
|-- templates/
|   |-- index.html          # Template utama halaman web
|-- static/
|   |-- styles.css          # File styling CSS
|   |-- script.js           # File JavaScript untuk interaktivitas
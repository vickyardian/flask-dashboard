"""
DASHBOARD PROGRAM IUP (INTERNATIONAL UNDERGRADUATE PROGRAM) PTN INDONESIA

Program ini adalah aplikasi web berbasis Flask yang menyediakan dashboard interaktif
untuk menganalisis data Program IUP di Perguruan Tinggi Negeri (PTN) Indonesia

FITUR UTAMA:
1. Statistik umum PTN dan program studi
2. Visualisasi data menggunakan grafik interaktif (Plotly)
3. Analisis distribusi geografis PTN
4. Detail program studi per PTN dengan grafik pie dan bar
5. Tabel data lengkap untuk setiap PTN
6. Interface responsif dan user-friendly

TEKNOLOGI YANG DIGUNAKAN:
- Flask: Framework web Python
- Pandas: Manipulasi dan analisis data
- Plotly: Visualisasi data interaktif
- HTML/CSS/JavaScript: Interface frontend
"""

# ==================== FILE: App.py ====================

# Import library yang diperlukan
from flask import Flask, render_template, request, jsonify  # Framework web Flask
import pandas as pd  # Library untuk manipulasi data
import plotly.express as px  # Library untuk membuat grafik dengan mudah
import plotly.graph_objects as go  # Library untuk grafik yang lebih kompleks
import json  # Library untuk menangani data JSON
import plotly  # Library utama Plotly
import os  # Library untuk mengakses variabel sistem
import numpy as np  # Library untuk operasi numerik

# Inisialisasi aplikasi Flask
app = Flask(__name__)

def format_rupiah(angka):
    """
    Fungsi untuk memformat angka menjadi format mata uang Rupiah Indonesia
    
    Parameter:
    - angka: nilai numerik yang akan diformat
    
    Return:
    - String dengan format "Rp1.000.000" (menggunakan titik sebagai pemisah ribuan)
    """
    # Cek apakah angka kosong atau NaN (Not a Number)
    if pd.isna(angka) or np.isnan(angka):
        return "Rp0"  # Kembalikan Rp0 jika data kosong
    
    # Format angka dengan pemisah titik untuk ribuan
    return f"Rp{int(angka):,}".replace(",", ".")

def load_data():
    """
    Fungsi untuk memuat dan membersihkan data dari file CSV
    
    Return:
    - DataFrame pandas yang sudah dibersihkan dan diformat
    """
    # Baca file CSV utama yang berisi data PTN
    df = pd.read_csv('MINI_TIM_B.csv')
    
    # Bersihkan kolom UKT dari karakter non-numerik (Rp, titik, koma)
    df['UKT'] = df['UKT'].replace('[Rp.,]', '', regex=True)
    
    # Konversi kolom UKT menjadi numerik, jika gagal akan menjadi NaN
    df['UKT'] = pd.to_numeric(df['UKT'], errors='coerce')
    
    # Konversi kolom DAYA TAMPUNG menjadi numerik
    df['DAYA TAMPUNG'] = pd.to_numeric(df['DAYA TAMPUNG'], errors='coerce')
    
    # Buat kolom baru untuk UKT yang sudah diformat dalam Rupiah
    df['UKT_RUPIAH'] = df['UKT'].apply(format_rupiah)
    
    return df

# Muat data saat aplikasi dimulai
df = load_data()

def create_chart(data, chart_type, title, x_col, y_col, **kwargs):
    """
    Fungsi untuk membuat berbagai jenis grafik
    
    Parameter:
    - data: DataFrame yang berisi data
    - chart_type: jenis grafik ('bar' atau 'pie')
    - title: judul grafik
    - x_col: nama kolom untuk sumbu X
    - y_col: nama kolom untuk sumbu Y
    - **kwargs: parameter tambahan untuk kustomisasi grafik
    
    Return:
    - Objek figure Plotly
    """
    if chart_type == 'bar':
        # Buat grafik batang menggunakan Plotly Express
        fig = px.bar(data, x=x_col, y=y_col, title=title, **kwargs)
        
        # Jika grafik horizontal, atur posisi teks dan urutan sumbu Y
        if 'orientation' in kwargs:
            fig.update_traces(textposition='outside')  # Teks di luar batang
            fig.update_layout(yaxis=dict(autorange="reversed"))  # Balik urutan Y
            
    elif chart_type == 'pie':
        # Buat grafik lingkaran menggunakan Plotly Express
        fig = px.pie(data, values=x_col, names=y_col, title=title, **kwargs)
    
    return fig

@app.route("/api/charts/<ptn>", methods=['GET'])
def get_charts(ptn):
    """
    API endpoint untuk mengambil data grafik dan statistik PTN tertentu
    
    Parameter:
    - ptn: nama PTN yang dipilih
    
    Return:
    - JSON berisi grafik pie, bar, data tabel, dan statistik rata-rata
    """
    try:
        # Filter data berdasarkan PTN yang dipilih
        ptn_data = df[df['PTN'] == ptn]
        
        # Cek apakah data PTN ditemukan
        if ptn_data.empty:
            return jsonify({'success': False, 'message': f'Data untuk {ptn} tidak ditemukan'})

        # HITUNG STATISTIK RATA-RATA
        # Hitung rata-rata daya tampung untuk PTN ini
        avg_daya_tampung = ptn_data['DAYA TAMPUNG'].mean()
        # Hitung rata-rata UKT untuk PTN ini
        avg_ukt = ptn_data['UKT'].mean()

        # FORMAT HASIL RATA-RATA UNTUK TAMPILAN
        # Format rata-rata daya tampung menjadi integer atau "N/A" jika kosong
        formatted_avg_daya_tampung = f"{int(avg_daya_tampung)}" if not pd.isna(avg_daya_tampung) else "N/A"
        # Format rata-rata UKT menjadi format Rupiah atau "N/A" jika kosong
        formatted_avg_ukt = format_rupiah(avg_ukt) if not pd.isna(avg_ukt) else "N/A"

        # PERSIAPAN DATA UNTUK GRAFIK PIE CHART (DAYA TAMPUNG)
        # Ambil kolom yang diperlukan dan hapus baris dengan data kosong
        data_daya = ptn_data[['JURUSAN', 'DAYA TAMPUNG']].dropna()
        
        if not data_daya.empty:
            # Buat grafik pie untuk distribusi daya tampung
            fig_daya = create_chart(data_daya, 'pie', f'Distribusi Daya Tampung di {ptn}', 
                                    'DAYA TAMPUNG', 'JURUSAN', hole=0.3)  # hole=0.3 untuk donut chart
        else:
            # Jika tidak ada data, buat grafik kosong dengan pesan
            fig_daya = px.pie(title=f'Tidak ada data daya tampung untuk {ptn}')
        
        # PERSIAPAN DATA UNTUK BAR CHART (UKT)
        # Ambil data UKT, hapus data kosong, dan urutkan dari kecil ke besar
        data_ukt = ptn_data[['JURUSAN', 'UKT']].dropna().sort_values('UKT', ascending=True)
        
        if not data_ukt.empty:
            # Buat grafik batang horizontal untuk UKT per program studi
            fig_ukt = create_chart(data_ukt, 'bar', f'UKT per Prodi di {ptn}',
                                   'UKT', 'JURUSAN', orientation='h')
            
            # Format label pada batang agar konsisten menggunakan titik sebagai pemisah
            fig_ukt.update_traces(texttemplate='Rp%{x:,.0f}'.replace(',', '.'))
            
            # Atur format sumbu-x agar tidak disingkat dan menggunakan format Rupiah
            fig_ukt.update_layout(
                xaxis_title="UKT",  # Label sumbu X
                xaxis_tickformat=',.0f',  # Format angka dengan pemisah ribuan
                separators='.,'  # Gunakan titik sebagai pemisah ribuan
            )
        else:
            # Jika tidak ada data UKT, buat grafik kosong
            fig_ukt = px.bar(title=f'Tidak ada data UKT untuk {ptn}')
        
        # PERSIAPAN DATA UNTUK TABEL
        # Pilih kolom yang diperlukan dan ganti nama kolom UKT_RUPIAH menjadi UKT
        filtered_for_table = ptn_data[['JURUSAN', 'DAYA TAMPUNG', 'UKT_RUPIAH']].rename(columns={'UKT_RUPIAH': 'UKT'})
        
        # Kembalikan semua data dalam format JSON
        return jsonify({
            'success': True,
            'pie_chart': json.dumps(fig_daya, cls=plotly.utils.PlotlyJSONEncoder),  # Grafik pie dalam JSON
            'bar_chart': json.dumps(fig_ukt, cls=plotly.utils.PlotlyJSONEncoder),   # Grafik bar dalam JSON
            'table_data': filtered_for_table.to_dict(orient='records'),            # Data tabel dalam array
            'avg_daya_tampung': formatted_avg_daya_tampung,                         # Rata-rata daya tampung
            'avg_ukt': formatted_avg_ukt                                            # Rata-rata UKT
        })
    except Exception as e:
        # Tangani error dan kembalikan pesan error
        return jsonify({'success': False, 'error': str(e)})

@app.route("/", methods=['GET'])
def index():
    """
    Route utama yang menampilkan halaman dashboard
    
    Return:
    - Template HTML dengan data statistik dan grafik
    """
    
    # PERSIAPAN DATA DASAR
    # Ambil daftar semua PTN dan urutkan secara alfabetis
    ptn_list = sorted(df['PTN'].unique())
    # Hitung jumlah PTN unik
    jumlah_ptn = df['PTN'].nunique()
    # Hitung jumlah jurusan per PTN dan urutkan berdasarkan nama PTN
    jurusan_per_ptn = df.groupby('PTN')['JURUSAN'].nunique().sort_index()

    # Bersihkan data dengan menghapus baris yang memiliki UKT atau DAYA TAMPUNG kosong
    df_clean = df.dropna(subset=['UKT', 'DAYA TAMPUNG'])
    
    # PERHITUNGAN STATISTIK UTAMA
    stats = {
        'jumlah_ptn': jumlah_ptn,                                    # Total PTN
        'jumlah_provinsi': df['PROVINSI'].nunique(),                 # Total provinsi
        'jumlah_kota': df['KOTA'].nunique(),                         # Total kota
        'total_prodi': len(df),                                      # Total program studi
        'provinsi_terbanyak': df.groupby('PROVINSI')['PTN'].nunique().sort_values(ascending=False).head(3)  # 3 provinsi dengan PTN terbanyak
    }
    
    # PEMBUATAN GRAFIK UTAMA
    charts = {}
    
    # 1. GRAFIK PROGRAM STUDI PALING POPULER
    # Hitung frekuensi kemunculan setiap jurusan di berbagai PTN
    jurusan_populer = df['JURUSAN'].value_counts().head(8).reset_index()
    jurusan_populer.columns = ['JURUSAN', 'JUMLAH_PTN']  # Ganti nama kolom
    
    # Buat grafik batang horizontal untuk program studi populer
    charts['popular'] = create_chart(jurusan_populer, 'bar', 'Program Studi Paling Populer',
                                   'JUMLAH_PTN', 'JURUSAN', orientation='h').to_html(full_html=False)
    
    # 2. GRAFIK PROGRAM STUDI DENGAN UKT TERTINGGI
    if not df_clean.empty:
        # Ambil program dengan UKT tertinggi dari setiap PTN
        ukt_termahal = df_clean.loc[df_clean.groupby('PTN')['UKT'].idxmax()][['PTN', 'JURUSAN', 'UKT']]
        # Urutkan berdasarkan UKT dari tertinggi dan ambil 5 teratas
        ukt_termahal_top = ukt_termahal.sort_values('UKT', ascending=False).head(5)
        # Buat label gabungan PTN + Jurusan
        ukt_termahal_top['LABEL'] = ukt_termahal_top['PTN'] + " - " + ukt_termahal_top['JURUSAN']
        
        # Buat grafik batang (dibalik urutannya untuk tampilan yang lebih baik)
        fig_ukt_tinggi = create_chart(ukt_termahal_top[::-1], 'bar', 'Program Studi dengan UKT Tertinggi', 'UKT', 'LABEL', orientation='h', color='JURUSAN')

        # Format teks pada batang menjadi format Rupiah
        fig_ukt_tinggi.update_traces(
            texttemplate='Rp%{x:,.0f}'.replace(',', '.'),  # Template format Rupiah
            textposition='outside'  # Posisi teks di luar batang
        )
        
        # Atur format sumbu X
        fig_ukt_tinggi.update_layout(
            xaxis_title="UKT (dalam Rupiah)",  # Label sumbu X
            xaxis_tickformat=',.0f',           # Format dengan pemisah ribuan
            separators='.,'                    # Gunakan titik sebagai pemisah
        )

        # Konversi grafik menjadi HTML
        charts['ukt_tinggi'] = fig_ukt_tinggi.to_html(full_html=False)
    
    # 3. GRAFIK PROGRAM DENGAN DAYA TAMPUNG TERBESAR
    # Ambil program dengan daya tampung terbesar dari setiap PTN
    daya_terbanyak = df_clean.loc[df_clean.groupby('PTN')['DAYA TAMPUNG'].idxmax()][['PTN', 'JURUSAN', 'DAYA TAMPUNG']]
    # Urutkan berdasarkan daya tampung dari terbesar dan ambil 5 teratas
    daya_terbanyak_top = daya_terbanyak.sort_values('DAYA TAMPUNG', ascending=False).head(5)
    
    # Buat grafik batang horizontal
    charts['kapasitas_besar'] = create_chart(daya_terbanyak_top, 'bar', 'Program Studi dengan Daya Tampung Terbesar', 'DAYA TAMPUNG', 'PTN', orientation='h', color='JURUSAN').to_html(full_html=False)
    
    # 4. GRAFIK DISTRIBUSI PTN PER PROVINSI
    # Hitung jumlah PTN per provinsi dan ambil 8 teratas
    provinsi_stats = df.groupby('PROVINSI')['PTN'].nunique().sort_values(ascending=False).head(8).reset_index()
    provinsi_stats.columns = ['PROVINSI', 'JUMLAH_PTN']  # Ganti nama kolom
    
    # Buat grafik batang horizontal
    charts['provinsi'] = create_chart(provinsi_stats, 'bar', 'Distribusi PTN per Provinsi',
                                    'JUMLAH_PTN', 'PROVINSI', orientation='h').to_html(full_html=False)
    
    # Render template HTML dengan semua data yang sudah dipersiapkan
    return render_template('index.html', 
                         stats=stats,           # Statistik umum
                         charts=charts,         # Semua grafik
                         jurusan_per_ptn=jurusan_per_ptn)  # Data jumlah jurusan per PTN

# Jalankan aplikasi Flask
if __name__ == "__main__":
    # Ambil port dari environment variable atau gunakan 5000 sebagai default
    port = int(os.environ.get("PORT", 5000))
    # Jalankan server pada semua interface (0.0.0.0) dengan debug mode aktif
    app.run(host="0.0.0.0", port=port, debug=True)
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import os
import numpy as np

app = Flask(__name__)

@app.route('/googled3d7408d119c4567.html')
def google_verify():
    return send_from_directory('static', 'googled3d7408d119c4567.html')

def format_rupiah(angka):
    # Handle NaN values
    if pd.isna(angka) or np.isnan(angka):
        return "Rp0"
    return f"Rp{int(angka):,}".replace(",", ".")

def load_data():
    df = pd.read_csv('MINI_TIM_B.csv')
    
    # Clean UKT column and handle NaN values
    df['UKT'] = df['UKT'].replace('[Rp.,]', '', regex=True)
    df['UKT'] = pd.to_numeric(df['UKT'], errors='coerce')  # Convert to numeric, NaN for invalid values
    
    # Handle DAYA TAMPUNG
    df['DAYA TAMPUNG'] = pd.to_numeric(df['DAYA TAMPUNG'], errors='coerce')
    
    # Apply format_rupiah function (now handles NaN)
    df['UKT_RUPIAH'] = df['UKT'].apply(format_rupiah)
    
    return df

df = load_data()

# Koordinat untuk setiap kota dalam dataset
KOORDINAT_KOTA = {
    'Semarang': {'lat': -6.9969, 'lon': 110.4209},
    'Jakarta': {'lat': -6.2088, 'lon': 106.8456},
    'Surabaya': {'lat': -7.2575, 'lon': 112.7521},
    'Yogyakarta': {'lat': -7.7956, 'lon': 110.3695},
    'Bandung': {'lat': -6.9175, 'lon': 107.6191},
    'Malang': {'lat': -7.9666, 'lon': 112.6326},
    'Bogor': {'lat': -6.5971, 'lon': 106.8060},
    'Jakarta Timur': {'lat': -6.2251, 'lon': 106.9004},
    'Purwokerto': {'lat': -7.4218, 'lon': 109.2343},
    'Surakarta': {'lat': -7.5755, 'lon': 110.8243},
    'Makassar': {'lat': -5.1477, 'lon': 119.4327},
    'Padang': {'lat': -0.9471, 'lon': 100.4172}
}

def create_map_data():
    """Membuat data untuk visualisasi peta"""
    # Filter out rows with NaN values for calculations
    df_clean = df.dropna(subset=['UKT', 'DAYA TAMPUNG'])
    
    # Agregasi data per kota
    kota_stats = df_clean.groupby(['KOTA', 'PROVINSI']).agg({
        'PTN': 'nunique',
        'JURUSAN': 'count',
        'DAYA TAMPUNG': 'sum',
        'UKT': 'mean'
    }).reset_index()
    
    # Tambahkan koordinat
    kota_stats['lat'] = kota_stats['KOTA'].map(lambda x: KOORDINAT_KOTA.get(x, {}).get('lat'))
    kota_stats['lon'] = kota_stats['KOTA'].map(lambda x: KOORDINAT_KOTA.get(x, {}).get('lon'))
    
    # Hapus kota yang tidak memiliki koordinat
    kota_stats = kota_stats.dropna(subset=['lat', 'lon'])
    
    # Format UKT rata-rata
    kota_stats['UKT_FORMAT'] = kota_stats['UKT'].apply(format_rupiah)
    
    return kota_stats

def create_map_visualization():
    """Membuat visualisasi peta Indonesia"""
    kota_stats = create_map_data()
    
    # Peta scatter dengan marker berdasarkan jumlah PTN
    fig_map = px.scatter_mapbox(
        kota_stats,
        lat='lat',
        lon='lon',
        size='PTN',
        color='JURUSAN',
        hover_name='KOTA',
        hover_data={
            'PROVINSI': True,
            'PTN': ':d',
            'JURUSAN': ':d',
            'DAYA TAMPUNG': ':,d',
            'UKT_FORMAT': True,
            'lat': False,
            'lon': False
        },
        title='Sebaran PTN Kelas Internasional di Indonesia',
        size_max=30,
        zoom=4,
        center={'lat': -2.5, 'lon': 118},
        color_continuous_scale='Viridis',
        labels={
            'PTN': 'Jumlah PTN',
            'JURUSAN': 'Jumlah Program Studi',
            'DAYA TAMPUNG': 'Total Daya Tampung',
            'UKT_FORMAT': 'Rata-rata UKT'
        }
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    return fig_map

def create_province_chart():
    """Membuat chart distribusi PTN per provinsi"""
    provinsi_stats = df.groupby('PROVINSI').agg({
        'PTN': 'nunique',
        'JURUSAN': 'count'
    }).reset_index().sort_values('PTN', ascending=False)
    
    fig_provinsi = px.bar(
        provinsi_stats,
        x='PTN',
        y='PROVINSI',
        orientation='h',
        title='Distribusi PTN Kelas Internasional per Provinsi',
        text='PTN',
        labels={'PTN': 'Jumlah PTN', 'PROVINSI': 'Provinsi'}
    )
    
    fig_provinsi.update_traces(textposition='outside')
    fig_provinsi.update_layout(
        yaxis=dict(autorange="reversed"),
        height=400
    )
    
    return fig_provinsi

def create_city_sunburst():
    """Membuat sunburst chart untuk hierarki Provinsi > Kota > PTN"""
    # Siapkan data untuk sunburst
    sunburst_data = df.groupby(['PROVINSI', 'KOTA', 'PTN']).size().reset_index(name='count')
    
    fig_sunburst = px.sunburst(
        sunburst_data,
        path=['PROVINSI', 'KOTA', 'PTN'],
        values='count',
        title='Hierarki Sebaran PTN: Provinsi → Kota → PTN',
        height=500
    )
    
    return fig_sunburst

# API endpoint untuk mendapatkan data chart berdasarkan PTN
@app.route("/api/charts/<ptn>", methods=['GET'])
def get_charts(ptn):
    try:
        # Filter data untuk PTN tertentu dan drop NaN values
        ptn_data = df[df['PTN'] == ptn]
        
        # 1. Pie Chart Daya Tampung
        data_daya = ptn_data[['JURUSAN', 'DAYA TAMPUNG']].dropna()
        if not data_daya.empty:
            fig_daya = px.pie(
                data_daya,
                values='DAYA TAMPUNG',
                names='JURUSAN',
                title=f'Distribusi Daya Tampung Prodi di {ptn}',
                hole=0.3
            )
            fig_daya.update_traces(textinfo='label+value', hovertemplate='%{label}<br>Daya Tampung: %{value:,}')
        else:
            fig_daya = px.pie(title=f'Tidak ada data daya tampung untuk {ptn}')
        
        # 2. Bar Chart UKT
        data_ukt = ptn_data[['JURUSAN', 'UKT']].dropna().sort_values('UKT', ascending=False)
        if not data_ukt.empty:
            fig_ukt = px.bar(
                data_ukt,
                x='UKT',
                y='JURUSAN',
                orientation='h',
                title=f'UKT Tiap Prodi di {ptn}',
                labels={'UKT': 'UKT (Rupiah)', 'JURUSAN': 'Prodi'},
                text='UKT'
            )
            fig_ukt.update_traces(
                hovertemplate='%{y}<br>UKT: Rp %{x:,.0f}',
                texttemplate='Rp %{x:,.0f}',
                textposition='outside'
            )
            fig_ukt.update_layout(
                xaxis_tickformat=',',
                xaxis=dict(tickprefix='Rp ')
            )
        else:
            fig_ukt = px.bar(title=f'Tidak ada data UKT untuk {ptn}')
        
        # 3. Data tabel detail
        filtered = ptn_data[['JURUSAN', 'DAYA TAMPUNG', 'UKT_RUPIAH']]
        
        return jsonify({
            'success': True,
            'pie_chart': json.dumps(fig_daya, cls=plotly.utils.PlotlyJSONEncoder),
            'bar_chart': json.dumps(fig_ukt, cls=plotly.utils.PlotlyJSONEncoder),
            'table_data': filtered.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route("/", methods=['GET'])
def index():
    ptn_list = sorted(df['PTN'].unique())

    # 1. Jumlah PTN dan jumlah jurusan
    jumlah_ptn = df['PTN'].nunique()
    jurusan_per_ptn = df.groupby('PTN')['JURUSAN'].nunique().sort_index()

    # Filter out NaN values for UKT-related calculations
    df_ukt_clean = df.dropna(subset=['UKT'])
    
    # 2.Prodi UKT Termahal dari PTN Berbeda
    if not df_ukt_clean.empty:
        ukt_termahal = df_ukt_clean.loc[df_ukt_clean.groupby('PTN')['UKT'].idxmax()][['PTN', 'JURUSAN', 'UKT']]
        ukt_termahal_top = ukt_termahal.sort_values('UKT', ascending=False).head(7)
        ukt_termahal_top['LABEL'] = ukt_termahal_top['PTN'] + " - " + ukt_termahal_top['JURUSAN']

        fig_ukt_termahal = px.bar(
            ukt_termahal_top[::-1],
            x='UKT',
            y='LABEL',
            orientation='h',
            title='Prodi dengan UKT Termahal dari PTN',
            text='UKT',
            labels={'UKT': 'UKT (Rupiah)', 'LABEL': 'PTN - Jurusan'}
        )
        fig_ukt_termahal.update_traces(
            hovertemplate='%{y}<br>UKT: Rp %{x:,.0f}',
            texttemplate='Rp %{x:,.0f}',
            textposition='outside'
        )
        fig_ukt_termahal.update_layout(
            xaxis_tickformat=',',
            xaxis=dict(tickprefix='Rp ')
        )
        chart_ukt_termahal = fig_ukt_termahal.to_html(full_html=False)
    else:
        chart_ukt_termahal = "<p>Tidak ada data UKT yang valid</p>"

    # Filter out NaN values for DAYA TAMPUNG calculations
    df_daya_clean = df.dropna(subset=['DAYA TAMPUNG'])
    
    # 3.Prodi Daya Tampung Terbanyak dari PTN Berbeda
    if not df_daya_clean.empty:
        df_sorted = df_daya_clean.sort_values(by=["PTN", "DAYA TAMPUNG"], ascending=[True, False])
        daya_terbanyak = df_sorted.loc[df_sorted.groupby("PTN")["DAYA TAMPUNG"].idxmax()].drop_duplicates(subset="PTN")
        daya_terbanyak_top7 = daya_terbanyak.sort_values("DAYA TAMPUNG", ascending=False).head(7)

        fig_daya_terbanyak = px.bar(
            daya_terbanyak_top7,
            x="DAYA TAMPUNG",
            y="PTN",
            color="JURUSAN",
            orientation="h",
            hover_data={"JURUSAN": True, "PTN": False, "DAYA TAMPUNG": True},
            title="Prodi dengan Daya Tampung Terbanyak dari PTN"
        )
        fig_daya_terbanyak.update_layout(
            xaxis_title="Daya Tampung",
            yaxis_title="PTN",
            yaxis=dict(autorange="reversed"),
            legend_title="JURUSAN"
        )
        chart_daya_terbanyak = fig_daya_terbanyak.to_html(full_html=False)
    else:
        chart_daya_terbanyak = "<p>Tidak ada data daya tampung yang valid</p>"

    # 4.Prodi UKT Termurah dari PTN Berbeda
    if not df_ukt_clean.empty:
        ukt_termurah = df_ukt_clean.loc[df_ukt_clean.groupby('PTN')['UKT'].idxmin()][['PTN', 'JURUSAN', 'UKT']]
        ukt_termurah_top = ukt_termurah.sort_values('UKT', ascending=True).head(7)
        ukt_termurah_top['LABEL'] = ukt_termurah_top['PTN'] + " - " + ukt_termurah_top['JURUSAN']

        fig_ukt_termurah = px.bar(
            ukt_termurah_top,
            x='UKT',
            y='LABEL',
            orientation='h',
            title='Prodi dengan UKT Termurah dari PTN',
            text='UKT',
            labels={'UKT': 'UKT (Rupiah)', 'LABEL': 'PTN - Jurusan'}
        )
        fig_ukt_termurah.update_traces(
            hovertemplate='%{y}<br>UKT: Rp %{x:,.0f}',
            texttemplate='Rp %{x:,.0f}',
            textposition='outside'
        )
        fig_ukt_termurah.update_layout(
            xaxis_tickformat=',',
            xaxis=dict(tickprefix='Rp ')
        )
        chart_ukt_termurah = fig_ukt_termurah.to_html(full_html=False)
    else:
        chart_ukt_termurah = "<p>Tidak ada data UKT yang valid</p>"

    # 5.Prodi Daya Tampung Terkecil dari PTN Berbeda
    if not df_daya_clean.empty:
        daya_terkecil = df_sorted.loc[df_sorted.groupby("PTN")["DAYA TAMPUNG"].idxmin()].drop_duplicates(subset="PTN")
        daya_terkecil_top7 = daya_terkecil.sort_values("DAYA TAMPUNG", ascending=True).head(7)

        fig_dayamin = px.bar(
            daya_terkecil_top7,
            x="DAYA TAMPUNG",
            y="PTN",
            color="JURUSAN",
            orientation="h",
            hover_data={"JURUSAN": True, "PTN": False, "DAYA TAMPUNG": True},
            title="Prodi dengan Daya Tampung Terkecil dari PTN"
        )
        fig_dayamin.update_layout(
            xaxis_title="Daya Tampung",
            yaxis_title="PTN",
            yaxis=dict(autorange="reversed"),
            legend_title="JURUSAN"
        )
        chart_dayamin = fig_dayamin.to_html(full_html=False)
    else:
        chart_dayamin = "<p>Tidak ada data daya tampung yang valid</p>"

    # 6.Jurusan Terpopuler
    jurusan_populer = df['JURUSAN'].value_counts().head(10).reset_index()
    jurusan_populer.columns = ['JURUSAN', 'JUMLAH_PTN']

    fig_popular = px.bar(
        jurusan_populer,
        x='JUMLAH_PTN',
        y='JURUSAN',
        orientation='h',
        title='Jurusan Terpopuler',
        labels={'JUMLAH_PTN': 'Jumlah PTN', 'JURUSAN': 'Jurusan'}
    )
    fig_popular.update_layout(yaxis=dict(autorange="reversed"))
    chart_popular = fig_popular.to_html(full_html=False)

    # 7. Visualisasi Peta Indonesia
    try:
        fig_map = create_map_visualization()
        chart_map = fig_map.to_html(full_html=False)
    except Exception as e:
        chart_map = f"<p>Error membuat peta: {str(e)}</p>"

    # 8. Chart Distribusi per Provinsi
    fig_provinsi = create_province_chart()
    chart_provinsi = fig_provinsi.to_html(full_html=False)

    # 9. Sunburst Chart
    fig_sunburst = create_city_sunburst()
    chart_sunburst = fig_sunburst.to_html(full_html=False)

    # 10. Statistik Geografis
    jumlah_provinsi = df['PROVINSI'].nunique()
    jumlah_kota = df['KOTA'].nunique()
    
    # Provinsi dengan PTN terbanyak
    provinsi_terbanyak = df.groupby('PROVINSI')['PTN'].nunique().sort_values(ascending=False)
    
    return render_template(
        'index.html',
        jumlah_ptn=jumlah_ptn,
        jurusan_per_ptn=jurusan_per_ptn,
        chart_ukt_termahal=chart_ukt_termahal,
        chart_daya_terbanyak=chart_daya_terbanyak,
        chart_ukt_termurah=chart_ukt_termurah,
        chart_dayamin=chart_dayamin,
        chart_popular=chart_popular,
        chart_map=chart_map,
        chart_provinsi=chart_provinsi,
        chart_sunburst=chart_sunburst,
        jumlah_provinsi=jumlah_provinsi,
        jumlah_kota=jumlah_kota,
        provinsi_terbanyak=provinsi_terbanyak
    )

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
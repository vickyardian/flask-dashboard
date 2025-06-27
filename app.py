from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
import os
import numpy as np

app = Flask(__name__)

def format_rupiah(angka):
    if pd.isna(angka) or np.isnan(angka):
        return "Rp0"
    return f"Rp{int(angka):,}".replace(",", ".")

def load_data():
    df = pd.read_csv('MINI_TIM_B.csv')
    df['UKT'] = df['UKT'].replace('[Rp.,]', '', regex=True)
    df['UKT'] = pd.to_numeric(df['UKT'], errors='coerce')
    df['DAYA TAMPUNG'] = pd.to_numeric(df['DAYA TAMPUNG'], errors='coerce')
    df['UKT_RUPIAH'] = df['UKT'].apply(format_rupiah)
    return df

df = load_data()

def create_chart(data, chart_type, title, x_col, y_col, **kwargs):
    """Unified function to create charts"""
    if chart_type == 'bar':
        fig = px.bar(data, x=x_col, y=y_col, title=title, **kwargs)
        if 'orientation' in kwargs:
            fig.update_traces(textposition='outside')
            fig.update_layout(yaxis=dict(autorange="reversed"))
    elif chart_type == 'pie':
        fig = px.pie(data, values=x_col, names=y_col, title=title, **kwargs)
    return fig

@app.route("/api/charts/<ptn>", methods=['GET'])
def get_charts(ptn):
    try:
        ptn_data = df[df['PTN'] == ptn]
        
        if ptn_data.empty:
            return jsonify({'success': False, 'message': f'Data untuk {ptn} tidak ditemukan'})

        # HITUNG RATA-RATA
        avg_daya_tampung = ptn_data['DAYA TAMPUNG'].mean()
        avg_ukt = ptn_data['UKT'].mean()

        # FORMAT HASIL RATA-RATA
        formatted_avg_daya_tampung = f"{int(avg_daya_tampung)}" if not pd.isna(avg_daya_tampung) else "N/A"
        formatted_avg_ukt = format_rupiah(avg_ukt) if not pd.isna(avg_ukt) else "N/A"

        # Pie Chart untuk Daya Tampung
        data_daya = ptn_data[['JURUSAN', 'DAYA TAMPUNG']].dropna()
        if not data_daya.empty:
            fig_daya = create_chart(data_daya, 'pie', f'Distribusi Daya Tampung di {ptn}', 
                                    'DAYA TAMPUNG', 'JURUSAN', hole=0.3)
        else:
            fig_daya = px.pie(title=f'Tidak ada data daya tampung untuk {ptn}')
        
        # Bar Chart untuk UKT
        data_ukt = ptn_data[['JURUSAN', 'UKT']].dropna().sort_values('UKT', ascending=True) # diubah ascending agar bar chart lebih rapi
        if not data_ukt.empty:
            fig_ukt = create_chart(data_ukt, 'bar', f'UKT per Prodi di {ptn}',
                                   'UKT', 'JURUSAN', orientation='h')
            
            # Memperbaiki format label di bar agar konsisten menggunakan titik
            fig_ukt.update_traces(texttemplate='Rp%{x:,.0f}'.replace(',', '.'))
            
            # Menambahkan format pada sumbu-x agar tidak disingkat
            fig_ukt.update_layout(
                xaxis_title="UKT",
                xaxis_tickformat=',.0f',
                separators='.,'
            )
        else:
            fig_ukt = px.bar(title=f'Tidak ada data UKT untuk {ptn}')
        
        # Data untuk tabel, menggunakan UKT_RUPIAH yang sudah diformat
        filtered_for_table = ptn_data[['JURUSAN', 'DAYA TAMPUNG', 'UKT_RUPIAH']].rename(columns={'UKT_RUPIAH': 'UKT'})
        
        return jsonify({
            'success': True,
            'pie_chart': json.dumps(fig_daya, cls=plotly.utils.PlotlyJSONEncoder),
            'bar_chart': json.dumps(fig_ukt, cls=plotly.utils.PlotlyJSONEncoder),
            'table_data': filtered_for_table.to_dict(orient='records'),
            'avg_daya_tampung': formatted_avg_daya_tampung,
            'avg_ukt': formatted_avg_ukt
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route("/", methods=['GET'])
def index():
    ptn_list = sorted(df['PTN'].unique())
    jumlah_ptn = df['PTN'].nunique()
    jurusan_per_ptn = df.groupby('PTN')['JURUSAN'].nunique().sort_index()

    # Clean data once
    df_clean = df.dropna(subset=['UKT', 'DAYA TAMPUNG'])
    
    # Key Statistics
    stats = {
        'jumlah_ptn': jumlah_ptn,
        'jumlah_provinsi': df['PROVINSI'].nunique(),
        'jumlah_kota': df['KOTA'].nunique(),
        'total_prodi': len(df),
        'provinsi_terbanyak': df.groupby('PROVINSI')['PTN'].nunique().sort_values(ascending=False).head(3) # Jumlah Provinsi dengan PTN Terbanyak
    }
    
    # Top Charts Only (Most Important)
    charts = {}
    
    # 1. Program studi populer
    jurusan_populer = df['JURUSAN'].value_counts().head(8).reset_index()
    jurusan_populer.columns = ['JURUSAN', 'JUMLAH_PTN']
    charts['popular'] = create_chart(jurusan_populer, 'bar', 'Program Studi Paling Populer',
                                   'JUMLAH_PTN', 'JURUSAN', orientation='h').to_html(full_html=False)
    
     # 2. Program studi UKT tertinggi
    if not df_clean.empty:
        ukt_termahal = df_clean.loc[df_clean.groupby('PTN')['UKT'].idxmax()][['PTN', 'JURUSAN', 'UKT']]
        ukt_termahal_top = ukt_termahal.sort_values('UKT', ascending=False).head(5)
        ukt_termahal_top['LABEL'] = ukt_termahal_top['PTN'] + " - " + ukt_termahal_top['JURUSAN']
        
        # 1. Buat objek grafik terlebih dahulu
        fig_ukt_tinggi = create_chart(ukt_termahal_top[::-1], 'bar', 'Program dengan UKT Tertinggi',
                                  'UKT', 'LABEL', orientation='h', color='JURUSAN')

        # 2. Terapkan format Rupiah pada teks bar dan hover
        fig_ukt_tinggi.update_traces(
            texttemplate='Rp%{x:,.0f}'.replace(',', '.'), 
            textposition='outside'
        )
        
         # 3. Ubah format sumbu x agar sesuai format Rupiah
        fig_ukt_tinggi.update_layout(
            xaxis_title="UKT (dalam Rupiah)",
            xaxis_tickformat=',.0f',
            separators='.,'
        )

        charts['ukt_tinggi'] = fig_ukt_tinggi.to_html(full_html=False)
    
    # 3. Largest Capacity Programs
    daya_terbanyak = df_clean.loc[df_clean.groupby('PTN')['DAYA TAMPUNG'].idxmax()][['PTN', 'JURUSAN', 'DAYA TAMPUNG']]
    daya_terbanyak_top = daya_terbanyak.sort_values('DAYA TAMPUNG', ascending=False).head(5)
    
    charts['kapasitas_besar'] = create_chart(daya_terbanyak_top, 'bar', 'Program dengan Daya Tampung Terbesar',
                                           'DAYA TAMPUNG', 'PTN', orientation='h', color='JURUSAN').to_html(full_html=False)
    
    # 4. Province Distribution
    provinsi_stats = df.groupby('PROVINSI')['PTN'].nunique().sort_values(ascending=False).head(8).reset_index()
    provinsi_stats.columns = ['PROVINSI', 'JUMLAH_PTN']
    charts['provinsi'] = create_chart(provinsi_stats, 'bar', 'Distribusi PTN per Provinsi',
                                    'JUMLAH_PTN', 'PROVINSI', orientation='h').to_html(full_html=False)
    
    return render_template('index.html', 
                         stats=stats,
                         charts=charts,
                         jurusan_per_ptn=jurusan_per_ptn)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
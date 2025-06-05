from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
import pandas as pd
import plotly.express as px
import json
import plotly

app = Flask(__name__)

@app.route('/googled3d7408d119c4567.html')
def google_verify():
    return send_from_directory('static', 'googled3d7408d119c4567.html')

def format_rupiah(angka):
    return f"Rp{int(angka):,}".replace(",", ".")

def load_data():
    df = pd.read_csv('MINI_TIM_B.csv')
    df['UKT'] = df['UKT'].replace('[Rp.,]', '', regex=True).astype(float)
    df['DAYA TAMPUNG'] = pd.to_numeric(df['DAYA TAMPUNG'], errors='coerce')
    df['UKT_RUPIAH'] = df['UKT'].apply(format_rupiah)
    return df

df = load_data()

# API endpoint untuk mendapatkan data chart berdasarkan PTN
@app.route("/api/charts/<ptn>", methods=['GET'])
def get_charts(ptn):
    try:
        # 1. Pie Chart Daya Tampung
        data_daya = df[df['PTN'] == ptn][['JURUSAN', 'DAYA TAMPUNG']].dropna()
        fig_daya = px.pie(
            data_daya,
            values='DAYA TAMPUNG',
            names='JURUSAN',
            title=f'Distribusi Daya Tampung Prodi di {ptn}',
            hole=0.3
        )
        fig_daya.update_traces(textinfo='label+value', hovertemplate='%{label}<br>Daya Tampung: %{value:,}')
        
        # 2. Bar Chart UKT
        data_ukt = df[df['PTN'] == ptn][['JURUSAN', 'UKT']].dropna().sort_values('UKT', ascending=False)
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
        
        # 3. Data tabel detail
        filtered = df[df['PTN'] == ptn][['JURUSAN', 'DAYA TAMPUNG', 'UKT_RUPIAH']]
        
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

    # 2.Prodi UKT Termahal dari PTN Berbeda
    ukt_termahal = df.loc[df.groupby('PTN')['UKT'].idxmax()][['PTN', 'JURUSAN', 'UKT']]
    ukt_termahal_top = ukt_termahal.sort_values('UKT', ascending=False).head(7)
    ukt_termahal_top['LABEL'] = ukt_termahal_top['PTN'] + " - " + ukt_termahal_top['JURUSAN']

    fig_ukt_termahal = px.bar(
        ukt_termahal_top[::-1],
        x='UKT',
        y='LABEL',
        orientation='h',
        title='7 Prodi dengan UKT Termahal dari PTN',
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

    # 3.Prodi Daya Tampung Terbanyak dari PTN Berbeda
    df_sorted = df.sort_values(by=["PTN", "DAYA TAMPUNG"], ascending=[True, False])
    daya_terbanyak = df_sorted.loc[df_sorted.groupby("PTN")["DAYA TAMPUNG"].idxmax()].drop_duplicates(subset="PTN")
    daya_terbanyak_top7 = daya_terbanyak.sort_values("DAYA TAMPUNG", ascending=False).head(7)

    fig_daya_terbanyak = px.bar(
        daya_terbanyak_top7,
        x="DAYA TAMPUNG",
        y="PTN",
        color="JURUSAN",
        orientation="h",
        hover_data={"JURUSAN": True, "PTN": False, "DAYA TAMPUNG": True},
        title="7 Prodi dengan Daya Tampung Terbanyak dari PTN"
    )
    fig_daya_terbanyak.update_layout(
        xaxis_title="Daya Tampung",
        yaxis_title="PTN",
        yaxis=dict(autorange="reversed"),
        legend_title="JURUSAN"
    )
    chart_daya_terbanyak = fig_daya_terbanyak.to_html(full_html=False)

    # 4.Prodi UKT Termurah dari PTN Berbeda
    ukt_termurah = df.loc[df.groupby('PTN')['UKT'].idxmin()][['PTN', 'JURUSAN', 'UKT']]
    ukt_termurah_top = ukt_termurah.sort_values('UKT', ascending=True).head(7)
    ukt_termurah_top['LABEL'] = ukt_termurah_top['PTN'] + " - " + ukt_termurah_top['JURUSAN']

    fig_ukt_termurah = px.bar(
        ukt_termurah_top,
        x='UKT',
        y='LABEL',
        orientation='h',
        title='7 Prodi dengan UKT Termurah dari PTN',
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

    # 5.Prodi Daya Tampung Terkecil dari PTN Berbeda
    daya_terkecil = df_sorted.loc[df_sorted.groupby("PTN")["DAYA TAMPUNG"].idxmin()].drop_duplicates(subset="PTN")
    daya_terkecil_top7 = daya_terkecil.sort_values("DAYA TAMPUNG", ascending=True).head(7)

    fig_dayamin = px.bar(
        daya_terkecil_top7,
        x="DAYA TAMPUNG",
        y="PTN",
        color="JURUSAN",
        orientation="h",
        hover_data={"JURUSAN": True, "PTN": False, "DAYA TAMPUNG": True},
        title="7 Prodi dengan Daya Tampung Terkecil dari PTN"
    )
    fig_dayamin.update_layout(
        xaxis_title="Daya Tampung",
        yaxis_title="PTN",
        yaxis=dict(autorange="reversed"),
        legend_title="JURUSAN"
    )
    chart_dayamin = fig_dayamin.to_html(full_html=False)

    # 6.Jurusan Terpopuler
    jurusan_populer = df['JURUSAN'].value_counts().head(10).reset_index()
    jurusan_populer.columns = ['JURUSAN', 'JUMLAH_PTN']

    fig_popular = px.bar(
        jurusan_populer,
        x='JUMLAH_PTN',
        y='JURUSAN',
        orientation='h',
        title='10 Jurusan Terpopuler',
        labels={'JUMLAH_PTN': 'Jumlah PTN', 'JURUSAN': 'Jurusan'}
    )
    fig_popular.update_layout(yaxis=dict(autorange="reversed"))
    chart_popular = fig_popular.to_html(full_html=False)

    return render_template(
        'index.html',
        jumlah_ptn=jumlah_ptn,
        jurusan_per_ptn=jurusan_per_ptn,
        chart_ukt_termahal=chart_ukt_termahal,
        chart_daya_terbanyak=chart_daya_terbanyak,
        chart_ukt_termurah=chart_ukt_termurah,
        chart_dayamin=chart_dayamin,
        chart_popular=chart_popular
    )

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

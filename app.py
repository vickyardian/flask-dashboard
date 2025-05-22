from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

def format_rupiah(angka):
    return f"Rp{int(angka):,}".replace(",", ".")

def load_data():
    df = pd.read_csv('MINI_TIM_B.csv')
    df['UKT'] = df['UKT'].replace('[Rp.,]', '', regex=True).astype(float)
    df['DAYA TAMPUNG'] = pd.to_numeric(df['DAYA TAMPUNG'], errors='coerce')
    df['UKT_RUPIAH'] = df['UKT'].apply(format_rupiah)
    return df

df = load_data()

@app.route("/", methods=['GET'])
def index():
    ptn_list = sorted(df['PTN'].unique())

    # Ambil parameter PTN dari URL untuk masing-masing visualisasi / tabel
    ptn_daya = request.args.get('ptn_daya', ptn_list[0])
    ptn_ukt = request.args.get('ptn_ukt', ptn_list[0])
    ptn_detail = request.args.get('ptn_detail', ptn_list[0])

    # 1. Jumlah PTN dan jumlah jurusan
    jumlah_ptn = df['PTN'].nunique()
    jurusan_per_ptn = df.groupby('PTN')['JURUSAN'].nunique().sort_index()

    # 2. Distribusi Daya Tampung per Prodi dalam PTN (Pie Chart)
    data_daya = df[df['PTN'] == ptn_daya][['JURUSAN', 'DAYA TAMPUNG']].dropna()
    fig_daya = px.pie(
        data_daya,
        values='DAYA TAMPUNG',
        names='JURUSAN',
        title=f'Distribusi Daya Tampung Prodi di {ptn_daya}',
        hole=0.3
    )
    fig_daya.update_traces(textinfo='label+value', hovertemplate='%{label}<br>Daya Tampung: %{value:,}')
    chart_daya = fig_daya.to_html(full_html=False)

    # 3. Distribusi UKT per Prodi dalam PTN (Bar Chart)
    data_ukt = df[df['PTN'] == ptn_ukt][['JURUSAN', 'UKT']].dropna().sort_values('UKT', ascending=False)
    fig_ukt = px.bar(
        data_ukt,
        x='UKT',
        y='JURUSAN',
        orientation='h',
        title=f'UKT Tiap Prodi di {ptn_ukt}',
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
    chart_ukt = fig_ukt.to_html(full_html=False)

    # 4. Tabel detail jurusan, daya tampung, dan UKT per PTN
    filtered = df[df['PTN'] == ptn_detail][['JURUSAN', 'DAYA TAMPUNG', 'UKT_RUPIAH']]

    # 5. 7 Prodi UKT Termahal dari PTN Berbeda
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

    # 6. 7 Prodi Daya Tampung Terbanyak dari PTN Berbeda
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

    # 7. 7 Prodi UKT Termurah dari PTN Berbeda
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

    # 8. 7 Prodi Daya Tampung Terkecil dari PTN Berbeda
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

    # 9. 10 Jurusan Terpopuler
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
        ptn_list=ptn_list,
        selected_ptn_daya=ptn_daya,
        selected_ptn_ukt=ptn_ukt,
        selected_ptn_detail=ptn_detail,
        chart_daya=chart_daya,
        chart_ukt=chart_ukt,
        filtered=filtered.to_dict(orient='records'),
        chart_ukt_termahal=chart_ukt_termahal,
        chart_daya_terbanyak=chart_daya_terbanyak,
        chart_ukt_termurah=chart_ukt_termurah,
        chart_dayamin=chart_dayamin,
        chart_popular=chart_popular
    )

if __name__ == "__main__":
    app.run(debug=True)

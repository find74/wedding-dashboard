import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# --- AUTO REFRESH setiap 6 jam ---
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=6 * 60 * 60 * 1000, key="autorefresh_6h")
except ImportError:
    pass

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="💍 42272",
    layout="wide",
    page_icon="💍",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Force Light Mode + Elegant Wedding Theme) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500&display=swap');

/* === FORCE LIGHT MODE — override OS dark mode === */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp, .main,
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebar"] ~ div {
    background-color: #fdfaf7 !important;
    color: #2c1810 !important;
}
.stApp {
    background: linear-gradient(135deg, #fdfaf7 0%, #f7f0e8 50%, #fdf6ee 100%) !important;
}
/* Force text dark on light */
p, span, div, li, td, th, label,
[data-testid="stMarkdownContainer"] * {
    color: #2c1810 !important;
}

/* Global font */
html, body, [class*="css"] { font-family: 'Jost', sans-serif; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c1810 0%, #4a2c20 100%) !important;
}
[data-testid="stSidebar"] * { color: #f0e4d4 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Jost', sans-serif;
    font-weight: 300;
    letter-spacing: 0.05em;
}

/* === HEADINGS === */
h1, h2, h3, h4 {
    font-family: 'Cormorant Garamond', serif !important;
    color: #2c1810 !important;
}

/* === METRIC CARDS === */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.85) !important;
    border: 1px solid #e8d5c0 !important;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="metric-container"] label {
    font-weight: 500;
    letter-spacing: 0.08em;
    font-size: 0.75em !important;
    text-transform: uppercase;
    color: #8b6f5c !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.8em !important;
    color: #2c1810 !important;
}

/* === DATAFRAME === */
[data-testid="stDataFrame"] {
    border: 1px solid #e8d5c0;
    border-radius: 12px;
    overflow: hidden;
}

/* === BUTTONS === */
.stButton > button {
    background: linear-gradient(135deg, #2c1810, #4a2c20) !important;
    color: #f0e4d4 !important;
    border: none;
    border-radius: 8px;
    font-family: 'Jost', sans-serif;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-size: 0.8em;
    padding: 0.5em 1.5em;
}
.stButton > button:hover { opacity: 0.85; }

/* === PROGRESS BAR === */
.stProgress > div > div {
    background: linear-gradient(90deg, #c9956b, #8b4513) !important;
}

/* === TABS === */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.6);
    border: 1px solid #e8d5c0;
    border-radius: 8px;
    color: #8b6f5c !important;
    font-family: 'Jost', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2c1810, #4a2c20) !important;
    color: #f0e4d4 !important;
}

/* === INPUTS === */
.stTextInput input, .stSelectbox > div {
    background: rgba(255,255,255,0.9) !important;
    color: #2c1810 !important;
    border: 1px solid #e8d5c0 !important;
    border-radius: 8px;
}

/* === RADIO === */
.stRadio label { color: #2c1810 !important; }

hr { border-color: #e8d5c0; }

/* === COUNTDOWN === */
.countdown-container {
    display: flex; gap: 16px; justify-content: center;
    flex-wrap: wrap; margin: 20px 0;
}
.countdown-box {
    background: linear-gradient(135deg, #2c1810, #4a2c20);
    border-radius: 16px; padding: 20px 24px; text-align: center;
    min-width: 90px; box-shadow: 0 8px 32px rgba(44,24,16,0.15);
}
.countdown-number {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3em; line-height: 1; display: block;
    font-weight: 300; color: #f0e4d4 !important;
}
.countdown-label {
    font-family: 'Jost', sans-serif; font-size: 0.65em;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: #c9a98a !important; display: block; margin-top: 4px;
}
.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8em; color: #2c1810 !important;
    text-align: center; margin-bottom: 4px;
}
.section-ornament {
    text-align: center; color: #c9956b !important;
    font-size: 1.2em; margin-bottom: 20px; letter-spacing: 0.3em;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIG — semua dari Streamlit Secrets
# ─────────────────────────────────────────────
SHEET_ID = st.secrets["SHEET_ID"]
GIDS = {
    "Budget":    st.secrets["GID_BUDGET"],
    "Tamu":      st.secrets["GID_TAMU"],
    "Todo":      st.secrets["GID_TODO"],
    "Seserahan": st.secrets["GID_SESERAHAN"],
}
WEDDING_DATE = date(2028, 12, 24)

# ─────────────────────────────────────────────
# GOOGLE SHEETS AUTH via Service Account
# ─────────────────────────────────────────────
@st.cache_resource
def get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=21600)  # Cache 6 jam
def load_sheet_as_df(sheet_id: str, gid: str, skip_rows: int = 0) -> pd.DataFrame:
    client = get_gspread_client()
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = next((ws for ws in spreadsheet.worksheets() if str(ws.id) == str(gid)), None)
    if worksheet is None:
        raise ValueError(f"Tab dengan GID {gid} tidak ditemukan.")
    all_values = worksheet.get_all_values()
    data    = all_values[skip_rows:]
    headers = data[0]
    rows    = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    df.columns = [str(c).strip() for c in df.columns]
    df.replace('', pd.NA, inplace=True)
    return df

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def clean_currency(val):
    if pd.isna(val) or str(val).strip() == "": return 0.0
    if isinstance(val, str):
        val = val.replace('Rp','').replace('.','').replace(',','').strip()
        try: return float(val)
        except: return 0.0
    try: return float(val)
    except: return 0.0

def clean_bool(val):
    if pd.isna(val): return False
    return str(val).strip().upper() in ['TRUE','CHECKED','1','1.0','V','YA','YES','✓']

def get_countdown():
    delta = WEDDING_DATE - date.today()
    d = delta.days
    if d < 0: return None, None, None, None
    return d, d // 365, (d % 365) // 30, (d % 365) % 30

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
load_error = None
try:
    df_budget = load_sheet_as_df(SHEET_ID, GIDS["Budget"], skip_rows=2)
    df_budget = df_budget.dropna(subset=['Detail'])
    df_budget['Actual_Num'] = df_budget['Actual'].apply(clean_currency)
    df_budget['Paid_Num']   = df_budget['Sudah Dibayarkan'].apply(clean_currency)
    df_budget['Sisa_Num']   = df_budget['Actual_Num'] - df_budget['Paid_Num']

    df_raw_tamu = load_sheet_as_df(SHEET_ID, GIDS["Tamu"], skip_rows=5)
    tamu_cols   = ['No','Nama','Instansi','Ket','Cetak','Digital','Hadir_H','Sblm_H','Keterangan']

    df_wanita = df_raw_tamu.iloc[:, 0:9].copy()
    df_wanita.columns = tamu_cols
    df_wanita = df_wanita.dropna(subset=['Nama'])
    df_wanita = df_wanita[df_wanita['Nama'].astype(str).str.strip().ne('')]

    df_pria = df_raw_tamu.iloc[:, 10:19].copy()
    df_pria.columns = tamu_cols
    df_pria = df_pria.dropna(subset=['Nama'])
    df_pria = df_pria[df_pria['Nama'].astype(str).str.strip().ne('')]

    df_all_guests = pd.concat([
        df_wanita.assign(Side='Wanita (CPW)'),
        df_pria.assign(Side='Pria (CPP)')
    ], ignore_index=True)

    df_todo_raw    = load_sheet_as_df(SHEET_ID, GIDS["Todo"], skip_rows=3)
    todo_check_col = df_todo_raw.columns[0]
    todo_name_col  = df_todo_raw.columns[1] if len(df_todo_raw.columns) > 1 else df_todo_raw.columns[0]
    df_todo = df_todo_raw.dropna(subset=[todo_name_col]).copy()
    df_todo['DONE'] = df_todo[todo_check_col].apply(clean_bool)
    df_todo = df_todo[df_todo[todo_name_col].astype(str).str.strip().ne('')]

    df_seserahan = load_sheet_as_df(SHEET_ID, GIDS["Seserahan"], skip_rows=2)
    df_seserahan = df_seserahan.dropna(subset=['LIST SESERAHAN'])
    df_seserahan['DONE_STATUS'] = df_seserahan['CHECKLIST'].apply(clean_bool)

except Exception as e:
    load_error = str(e)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:20px 0 10px 0;'>
    <div style='font-size:2em;margin-bottom:4px;'>💍</div>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.3em;color:#f0e4d4;letter-spacing:0.05em;'>
        42272
    </div>
    <div style='font-size:0.7em;color:#c9a98a;letter-spacing:0.15em;text-transform:uppercase;margin-top:4px;'>
        24 Desember 2028
    </div>
</div>
<hr style='border-color:#6b4c3b;margin:10px 0 20px 0;'>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasi",
    ["🏠 Overview","💰 Anggaran & Vendor","👥 Tamu Undangan","📝 Persiapan"],
    label_visibility="collapsed")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(f"""
<div style='text-align:center;font-size:0.65em;color:#8b6f5c;padding-top:20px;'>
    Auto-refresh setiap 6 jam<br>
    <span style='color:#c9956b;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ERROR STATE
# ─────────────────────────────────────────────
if load_error:
    st.error(f"⚠️ Gagal membaca data: {load_error}")
    st.info("Pastikan: (1) Service Account sudah di-share ke Google Sheet, (2) Semua Secrets sudah diisi di Streamlit Cloud.")
    st.stop()

# =========================================================
# OVERVIEW
# =========================================================
if menu == "🏠 Overview":
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px 0;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:3em;color:#2c1810;line-height:1.1;'>
            42272</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.1em;color:#8b6f5c;
             letter-spacing:0.3em;text-transform:uppercase;margin-top:4px;'>
            Wedding Command Center</div>
        <div style='color:#c9956b;font-size:1.4em;letter-spacing:0.4em;margin:8px 0;'>✦ ✦ ✦</div>
    </div>""", unsafe_allow_html=True)

    days_total, years, months, remaining_days = get_countdown()
    if days_total is not None:
        st.markdown(f"""
        <div style='text-align:center;font-family:Jost,sans-serif;font-size:0.75em;
             letter-spacing:0.2em;text-transform:uppercase;color:#8b6f5c;margin-bottom:12px;'>
            Menuju Hari Bahagia</div>
        <div class="countdown-container">
            <div class="countdown-box"><span class="countdown-number">{days_total}</span><span class="countdown-label">Total Hari</span></div>
            <div class="countdown-box"><span class="countdown-number">{years}</span><span class="countdown-label">Tahun</span></div>
            <div class="countdown-box"><span class="countdown-number">{months}</span><span class="countdown-label">Bulan</span></div>
            <div class="countdown-box"><span class="countdown-number">{remaining_days}</span><span class="countdown-label">Hari</span></div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;font-size:2em;color:#c9956b;padding:20px;">🎊 Selamat Hari Pernikahan! 🎊</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="section-title">Tamu Undangan</div><div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("👩 Tamu CPW", f"{len(df_wanita):,} orang")
    c2.metric("👨 Tamu CPP", f"{len(df_pria):,} orang")
    c3.metric("👥 Total",    f"{len(df_all_guests):,} orang")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Anggaran</div><div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)
    total_b = df_budget['Actual_Num'].sum()
    paid_b  = df_budget['Paid_Num'].sum()
    sisa_b  = df_budget['Sisa_Num'].sum()
    b1,b2,b3 = st.columns(3)
    b1.metric("Total Anggaran", f"Rp {total_b:,.0f}")
    b2.metric("Sudah Dibayar",  f"Rp {paid_b:,.0f}")
    b3.metric("Sisa Utang",     f"Rp {sisa_b:,.0f}")
    pv = paid_b/total_b if total_b>0 else 0
    st.markdown(f"<div style='font-size:0.8em;color:#8b6f5c;margin-bottom:4px;'>Progres Pelunasan: {pv*100:.1f}%</div>", unsafe_allow_html=True)
    st.progress(pv)
    st.markdown("<br>", unsafe_allow_html=True)

    done_count = df_todo['DONE'].sum()
    total_todo = len(df_todo)
    tp = done_count/total_todo if total_todo>0 else 0
    st.markdown('<div class="section-title">To-Do List</div><div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)
    t1,t2,t3 = st.columns(3)
    t1.metric("Total Task", f"{total_todo} item")
    t2.metric("✅ Selesai", f"{int(done_count)} item")
    t3.metric("⏳ Belum",   f"{total_todo-int(done_count)} item")
    st.markdown(f"<div style='font-size:0.8em;color:#8b6f5c;margin-bottom:4px;'>Progres To-Do: {tp*100:.1f}%</div>", unsafe_allow_html=True)
    st.progress(float(tp))

# =========================================================
# ANGGARAN
# =========================================================
elif menu == "💰 Anggaran & Vendor":
    st.markdown('<h1 style="text-align:center;">Anggaran & Vendor</h1>', unsafe_allow_html=True)
    st.markdown('<div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)

    total_b=df_budget['Actual_Num'].sum(); paid_b=df_budget['Paid_Num'].sum(); sisa_b=df_budget['Sisa_Num'].sum()
    c1,c2,c3=st.columns(3)
    c1.metric("Total Anggaran",f"Rp {total_b:,.0f}")
    c2.metric("Sudah Dibayar", f"Rp {paid_b:,.0f}")
    c3.metric("Sisa Utang",    f"Rp {sisa_b:,.0f}")
    st.markdown("<br>", unsafe_allow_html=True)

    cl,cr=st.columns(2)
    with cl:
        df_pie=df_budget[df_budget['Actual_Num']>0].copy()
        fig=px.pie(df_pie,values='Actual_Num',names='Detail',title="Distribusi Anggaran",hole=0.45,
                   color_discrete_sequence=px.colors.sequential.Oryel)
        fig.update_layout(font_family="Jost",paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                          title_font_family="Cormorant Garamond",title_font_size=20)
        st.plotly_chart(fig,use_container_width=True)
    with cr:
        df_bar=df_budget[df_budget['Actual_Num']>0].copy()
        fig2=go.Figure()
        fig2.add_trace(go.Bar(name='Sudah Dibayar',x=df_bar['Detail'],y=df_bar['Paid_Num'],marker_color='#8b4513'))
        fig2.add_trace(go.Bar(name='Sisa Bayar',   x=df_bar['Detail'],y=df_bar['Sisa_Num'],marker_color='#e8d5c0'))
        fig2.update_layout(barmode='stack',title='Status Pelunasan per Vendor',font_family="Jost",
                           paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                           title_font_family="Cormorant Garamond",title_font_size=20,
                           xaxis=dict(tickangle=-30),legend=dict(orientation='h',y=-0.25))
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown("#### Detail Tabel Vendor")
    dcols=[c for c in ['Detail','Vendor','Actual','Sudah Dibayarkan','Sisa Pembayaran','Payment'] if c in df_budget.columns]
    st.dataframe(df_budget[dcols],use_container_width=True,hide_index=True)

# =========================================================
# TAMU
# =========================================================
elif menu == "👥 Tamu Undangan":
    st.markdown('<h1 style="text-align:center;">Tamu Undangan</h1>', unsafe_allow_html=True)
    st.markdown('<div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)

    c1,c2,c3=st.columns(3)
    c1.metric("👩 CPW",f"{len(df_wanita):,} orang")
    c2.metric("👨 CPP",f"{len(df_pria):,} orang")
    c3.metric("👥 Total",f"{len(df_all_guests):,} orang")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### 🔍 Cari & Filter Tamu")
    sc,fc=st.columns([3,1])
    with sc:
        q=st.text_input("Cari",placeholder="Nama atau instansi...",label_visibility="collapsed")
    with fc:
        sf=st.selectbox("Side",["Semua","Wanita (CPW)","Pria (CPP)"],label_visibility="collapsed")

    df_f=df_all_guests.copy()
    if q:
        df_f=df_f[df_f['Nama'].astype(str).str.lower().str.contains(q.lower(),na=False)|
                  df_f['Instansi'].astype(str).str.lower().str.contains(q.lower(),na=False)]
    if sf!="Semua":
        df_f=df_f[df_f['Side']==sf]

    st.markdown(f"<div style='font-size:0.85em;color:#8b6f5c;margin-bottom:8px;'>Menampilkan {len(df_f)} tamu</div>", unsafe_allow_html=True)
    dtcols=[c for c in ['Nama','Instansi','Ket','Side'] if c in df_f.columns]
    st.dataframe(df_f[dtcols],use_container_width=True,hide_index=True,height=450)

    if 'Instansi' in df_all_guests.columns:
        ic=df_all_guests['Instansi'].dropna().value_counts().head(10).reset_index()
        ic.columns=['Instansi','Jumlah']
        fig3=px.bar(ic,x='Jumlah',y='Instansi',orientation='h',title='Top 10 Instansi',
                    color='Jumlah',color_continuous_scale='Oryel')
        fig3.update_layout(font_family="Jost",paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                           title_font_family="Cormorant Garamond",title_font_size=20,
                           yaxis=dict(autorange="reversed"),showlegend=False,coloraxis_showscale=False)
        st.plotly_chart(fig3,use_container_width=True)

# =========================================================
# PERSIAPAN
# =========================================================
elif menu == "📝 Persiapan":
    st.markdown('<h1 style="text-align:center;">Persiapan Pernikahan</h1>', unsafe_allow_html=True)
    st.markdown('<div class="section-ornament">— ✦ —</div>', unsafe_allow_html=True)

    tab1,tab2=st.tabs(["📋 To-Do List","🎁 Seserahan"])

    with tab1:
        dc=int(df_todo['DONE'].sum()); tt=len(df_todo); tp=dc/tt if tt>0 else 0
        m1,m2,m3=st.columns(3)
        m1.metric("Total",f"{tt}"); m2.metric("✅ Selesai",f"{dc}"); m3.metric("⏳ Belum",f"{tt-dc}")
        st.markdown(f"**Progres: {tp*100:.1f}%**"); st.progress(float(tp))
        st.markdown("<br>", unsafe_allow_html=True)
        tf=st.radio("Tampilkan:",["Semua","Belum Selesai","Sudah Selesai"],horizontal=True)
        dtd=df_todo.copy()
        if tf=="Belum Selesai": dtd=dtd[dtd['DONE']==False]
        elif tf=="Sudah Selesai": dtd=dtd[dtd['DONE']==True]
        dtd['Status']=dtd['DONE'].map({True:'✅ Selesai',False:'⏳ Belum'})
        acols=[c for c in dtd.columns if c not in ['DONE'] and not str(c).startswith('Unnamed')][:3]
        sc2=acols+['Status']
        sc2=[c for c in sc2 if c in dtd.columns]
        st.dataframe(dtd[sc2],use_container_width=True,hide_index=True,height=400)

    with tab2:
        ds=int(df_seserahan['DONE_STATUS'].sum()); ts=len(df_seserahan); sp=ds/ts if ts>0 else 0
        s1,s2,s3=st.columns(3)
        s1.metric("Total",f"{ts}"); s2.metric("✅ Siap",f"{ds}"); s3.metric("⏳ Belum",f"{ts-ds}")
        st.markdown(f"**Progres: {sp*100:.1f}%**"); st.progress(float(sp))
        st.markdown("<br>", unsafe_allow_html=True)
        sff=st.radio("Tampilkan:",["Semua","Belum Siap","Sudah Siap"],horizontal=True,key="ses_filter")
        dsd=df_seserahan.copy()
        if sff=="Belum Siap": dsd=dsd[dsd['DONE_STATUS']==False]
        elif sff=="Sudah Siap": dsd=dsd[dsd['DONE_STATUS']==True]
        dsd['Status']=dsd['DONE_STATUS'].map({True:'✅ Siap',False:'⏳ Belum'})
        scc=[c for c in ['LIST SESERAHAN','DETAIL','Status'] if c in dsd.columns]
        st.dataframe(dsd[scc],use_container_width=True,hide_index=True,height=400)
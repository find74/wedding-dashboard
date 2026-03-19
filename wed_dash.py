import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# ── AUTO REFRESH 6 JAM ──────────────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=6 * 60 * 60 * 1000, key="auto6h")
except ImportError:
    pass

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💍 42272",
    layout="wide",
    page_icon="💍",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Jost:wght@300;400;500&display=swap');

html, body, [class*="css"], .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"] {
    font-family: 'Jost', sans-serif !important;
    background-color: #fdfaf7 !important;
    color: #2c1810 !important;
}
.stApp {
    background: linear-gradient(135deg,#fdfaf7 0%,#f7f0e8 50%,#fdf6ee 100%) !important;
}
/* force text on main content */
p, span, div, li, td, th,
[data-testid="stMarkdownContainer"] * { color: #2c1810 !important; }
h1,h2,h3,h4 { font-family:'Cormorant Garamond',serif !important; color:#2c1810 !important; }

/* sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#2c1810 0%,#4a2c20 100%) !important;
}
[data-testid="stSidebar"] * { color:#f0e4d4 !important; }

/* metrics */
[data-testid="metric-container"] {
    background:rgba(255,255,255,0.85) !important;
    border:1px solid #e8d5c0 !important;
    border-radius:12px; padding:16px;
}
[data-testid="metric-container"] label {
    font-size:0.72em !important; text-transform:uppercase;
    letter-spacing:0.08em; color:#8b6f5c !important;
}
[data-testid="stMetricValue"] {
    font-family:'Cormorant Garamond',serif !important;
    font-size:1.7em !important; color:#2c1810 !important;
}

/* dataframe */
[data-testid="stDataFrame"] { border:1px solid #e8d5c0; border-radius:12px; overflow:hidden; }

/* buttons */
.stButton>button {
    background:linear-gradient(135deg,#2c1810,#4a2c20) !important;
    color:#f0e4d4 !important; border:none; border-radius:8px;
    font-family:'Jost',sans-serif; letter-spacing:0.1em;
    text-transform:uppercase; font-size:0.78em; padding:0.5em 1.5em;
}
/* progress */
.stProgress>div>div { background:linear-gradient(90deg,#c9956b,#8b4513) !important; }

/* tabs */
.stTabs [data-baseweb="tab"] {
    background:rgba(255,255,255,0.55); border:1px solid #e8d5c0;
    border-radius:8px; color:#8b6f5c !important; font-family:'Jost',sans-serif;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#2c1810,#4a2c20) !important;
    color:#f0e4d4 !important;
}

/* inputs */
.stTextInput input,.stSelectbox>div {
    background:rgba(255,255,255,0.9) !important;
    color:#2c1810 !important; border:1px solid #e8d5c0 !important; border-radius:8px;
}
.stRadio label { color:#2c1810 !important; }
hr { border-color:#e8d5c0; }

/* ── custom components ── */
.countdown-container { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin:16px 0; }
.countdown-box {
    background:linear-gradient(135deg,#2c1810,#4a2c20);
    border-radius:14px; padding:18px 22px; text-align:center; min-width:84px;
    box-shadow:0 6px 24px rgba(44,24,16,0.13);
}
.cd-num { font-family:'Cormorant Garamond',serif; font-size:2.8em; line-height:1;
          display:block; font-weight:300; color:#f0e4d4 !important; }
.cd-lbl { font-family:'Jost',sans-serif; font-size:0.62em; letter-spacing:0.15em;
          text-transform:uppercase; color:#c9a98a !important; display:block; margin-top:3px; }

.sec-title { font-family:'Cormorant Garamond',serif; font-size:1.75em;
             color:#2c1810 !important; text-align:center; margin-bottom:2px; }
.sec-orn   { text-align:center; color:#c9956b !important; font-size:1.1em;
             margin-bottom:18px; letter-spacing:0.3em; }

.badge-done  { background:#d4edda; color:#155724 !important; padding:2px 10px;
               border-radius:20px; font-size:0.78em; font-weight:500; }
.badge-pend  { background:#fff3cd; color:#856404 !important; padding:2px 10px;
               border-radius:20px; font-size:0.78em; font-weight:500; }
.badge-miss  { background:#f8d7da; color:#721c24 !important; padding:2px 10px;
               border-radius:20px; font-size:0.78em; font-weight:500; }
.info-box {
    background:rgba(255,255,255,0.7); border:1px solid #e8d5c0;
    border-radius:12px; padding:16px 20px; margin:10px 0;
}
</style>
""", unsafe_allow_html=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────
try:
    SHEET_ID = st.secrets["SHEET_ID"]
    GIDS = {
        "Start":      st.secrets["GID_START"],
        "Budget":     st.secrets["GID_BUDGET"],
        "Budgeting":  st.secrets["GID_BUDGETING"],
        "Seserahan":  st.secrets["GID_SESERAHAN"],
        "Todo":       st.secrets["GID_TODO"],
        "Tamu":       st.secrets["GID_TAMU"],
        "Playlist":   st.secrets["GID_PLAYLIST"],
    }
    USE_SERVICE_ACCOUNT = True
except Exception:
    # Fallback: public CSV (untuk testing)
    SHEET_ID = "1vfMBjDcu5vqbcKLAWGriDA89S3bbjkUH8mSU3GLrEs0"
    GIDS = {
        "Start":      "180476786",
        "Budget":     "771919678",
        "Budgeting":  "1724463210",   # <- ini placeholder, sesuaikan
        "Seserahan":  "1333161294",
        "Todo":       "39054956",
        "Tamu":       "1724463210",
        "Playlist":   "0",
    }
    USE_SERVICE_ACCOUNT = False

WEDDING_DATE = date(2028, 12, 24)

# ── AUTH ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=21600)
def load_sheet_raw(sheet_id: str, gid: str) -> list:
    """Return raw list of rows (list of lists) dari Google Sheet."""
    client = get_gspread_client()
    ws = next((w for w in client.open_by_key(sheet_id).worksheets()
               if str(w.id) == str(gid)), None)
    if ws is None:
        return []
    return ws.get_all_values()

def rows_to_df(all_rows: list, header_row: int, data_start: int, data_end: int = None) -> pd.DataFrame:
    """Convert slice of rows into DataFrame."""
    if not all_rows or header_row >= len(all_rows):
        return pd.DataFrame()
    headers = [str(c).strip() for c in all_rows[header_row]]
    end = data_end if data_end else len(all_rows)
    rows = all_rows[data_start:end]
    # Pad rows yang lebih pendek
    rows = [r + [''] * (len(headers) - len(r)) for r in rows]
    rows = [r[:len(headers)] for r in rows]
    df = pd.DataFrame(rows, columns=headers)
    df.replace('', pd.NA, inplace=True)
    return df

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clean_currency(val):
    if pd.isna(val) or str(val).strip() == "": return 0.0
    if isinstance(val, str):
        v = val.replace('Rp','').replace('.','').replace(',','').strip()
        try: return float(v)
        except: return 0.0
    try: return float(val)
    except: return 0.0

def clean_bool(val):
    if pd.isna(val): return False
    return str(val).strip().upper() in ['TRUE','CHECKED','1','1.0','V','YA','YES','✓','SELESAI']

def fmt_rp(v): return f"Rp {v:,.0f}"

def get_countdown():
    d = (WEDDING_DATE - date.today()).days
    if d < 0: return None,None,None,None
    return d, d//365, (d%365)//30, (d%365)%30

def progress_bar_html(pct, label=""):
    color = "#8b4513" if pct < 50 else "#c9956b" if pct < 80 else "#2d7a2d"
    return f"""
    <div style='margin:6px 0 14px;'>
        <div style='display:flex;justify-content:space-between;font-size:0.78em;color:#8b6f5c;margin-bottom:4px;'>
            <span>{label}</span><span>{pct:.1f}%</span>
        </div>
        <div style='background:#e8d5c0;border-radius:8px;height:10px;'>
            <div style='background:{color};width:{pct:.1f}%;height:10px;border-radius:8px;transition:width 0.5s;'></div>
        </div>
    </div>"""

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
err = None
try:
    # ── BUDGET (sheet2, header row=2, data row=3..29) ──────────────────────
    raw_budget = load_sheet_raw(SHEET_ID, GIDS["Budget"])
    df_budget = rows_to_df(raw_budget, header_row=2, data_start=3, data_end=29)
    df_budget = df_budget.dropna(subset=['Detail'])
    df_budget = df_budget[df_budget['Detail'].astype(str).str.strip() != '']
    df_budget['Actual_Num'] = df_budget['Actual'].apply(clean_currency)
    df_budget['Paid_Num']   = df_budget['Sudah Dibayarkan'].apply(clean_currency)
    df_budget['Sisa_Num']   = df_budget['Actual_Num'] - df_budget['Paid_Num']
    df_budget['DP_Num']     = df_budget['DP/Uang Muka'].apply(clean_currency) if 'DP/Uang Muka' in df_budget.columns else 0

    # ── ENGAGEMENT BUDGETING (sheet3, header row=9, data row=10..33) ───────
    raw_budgeting = load_sheet_raw(SHEET_ID, GIDS["Budgeting"])
    # Tab Budgeting punya GID yang sama dengan Tamu di fallback — skip kalau sama
    df_engagement = rows_to_df(raw_budgeting, header_row=9, data_start=10, data_end=34)
    if 'ITEM' in df_engagement.columns:
        df_engagement = df_engagement.dropna(subset=['ITEM'])
        df_engagement = df_engagement[df_engagement['ITEM'].astype(str).str.strip() != '']
        df_engagement['Budget_Num'] = df_engagement['BUDGET'].apply(clean_currency) if 'BUDGET' in df_engagement.columns else 0
        df_engagement['Actual_Num'] = df_engagement['ACTUAL'].apply(clean_currency) if 'ACTUAL' in df_engagement.columns else 0
    else:
        df_engagement = pd.DataFrame()

    # ── SESERAHAN — 3 tabel dalam 1 tab ───────────────────────────────────
    raw_ses = load_sheet_raw(SHEET_ID, GIDS["Seserahan"])

    # Tabel 1: Seserahan (header row=2, data row=3..35)
    df_seserahan = rows_to_df(raw_ses, header_row=2, data_start=3, data_end=36)
    if 'LIST SESERAHAN' in df_seserahan.columns:
        df_seserahan = df_seserahan.dropna(subset=['LIST SESERAHAN'])
        df_seserahan = df_seserahan[df_seserahan['LIST SESERAHAN'].astype(str).str.strip() != '']
        df_seserahan['DONE'] = df_seserahan['CHECKLIST'].apply(clean_bool) if 'CHECKLIST' in df_seserahan.columns else False
        df_seserahan['Normal_Num'] = df_seserahan['NORMAL PRICE'].apply(clean_currency) if 'NORMAL PRICE' in df_seserahan.columns else 0
        df_seserahan['Final_Num']  = df_seserahan['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_seserahan.columns else 0

    # Tabel 2: Mahar (header row=40, data row=41..46)
    df_mahar = rows_to_df(raw_ses, header_row=40, data_start=41, data_end=47)
    if 'LIST MAHAR' in df_mahar.columns:
        df_mahar = df_mahar.dropna(subset=['LIST MAHAR'])
        df_mahar = df_mahar[df_mahar['LIST MAHAR'].astype(str).str.strip() != '']
        df_mahar['DONE'] = df_mahar['CHECKLIST'].apply(clean_bool) if 'CHECKLIST' in df_mahar.columns else False
        df_mahar['Est_Num']   = df_mahar['ESTIMASI'].apply(clean_currency) if 'ESTIMASI' in df_mahar.columns else 0
        df_mahar['Final_Num'] = df_mahar['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_mahar.columns else 0
    else:
        df_mahar = pd.DataFrame(columns=['LIST MAHAR','DONE'])

    # Tabel 3: Hias Seserahan (header row=48, data row=49..58)
    df_hias = rows_to_df(raw_ses, header_row=48, data_start=49, data_end=59)
    if 'LIST' in df_hias.columns:
        df_hias = df_hias.dropna(subset=['LIST'])
        df_hias = df_hias[df_hias['LIST'].astype(str).str.strip() != '']
        df_hias['DONE'] = df_hias['CHECKLIS'].apply(clean_bool) if 'CHECKLIS' in df_hias.columns else False
        df_hias['Est_Num']   = df_hias['ESTIMASI'].apply(clean_currency) if 'ESTIMASI' in df_hias.columns else 0
        df_hias['Final_Num'] = df_hias['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_hias.columns else 0
    else:
        df_hias = pd.DataFrame(columns=['LIST','DONE'])

    # ── TODO — 2 tabel ────────────────────────────────────────────────────
    raw_todo = load_sheet_raw(SHEET_ID, GIDS["Todo"])
    # Tabel 1: Gantt tasks (header row=3, col A=No, col B=Kegiatan, AL=DP, AM=Full Pay)
    df_tasks = rows_to_df(raw_todo, header_row=3, data_start=6, data_end=28)
    if len(df_tasks.columns) >= 2:
        col_no  = df_tasks.columns[0]
        col_keg = df_tasks.columns[1]
        # DP dan Full Payment ada di kolom 37 (AL) dan 38 (AM)
        col_dp  = df_tasks.columns[37] if len(df_tasks.columns) > 37 else None
        col_fp  = df_tasks.columns[38] if len(df_tasks.columns) > 38 else None
        df_tasks = df_tasks.dropna(subset=[col_keg])
        df_tasks = df_tasks[df_tasks[col_keg].astype(str).str.strip() != '']
        df_tasks = df_tasks.rename(columns={col_no:'No', col_keg:'Kegiatan'})
        if col_dp: df_tasks['DP_Done']  = df_tasks[col_dp].apply(clean_bool)
        if col_fp: df_tasks['FP_Done']  = df_tasks[col_fp].apply(clean_bool)
    else:
        df_tasks = pd.DataFrame(columns=['No','Kegiatan'])

    # Tabel 2: KUA Dokumen (header row=29, data row=30..43)
    df_kua = rows_to_df(raw_todo, header_row=29, data_start=30, data_end=44)
    if len(df_kua.columns) >= 2:
        col_item   = df_kua.columns[1] if len(df_kua.columns) > 1 else df_kua.columns[0]
        col_status = None
        for c in df_kua.columns:
            if 'status' in str(c).lower() or 'J' == c:
                col_status = c; break
        if col_status is None and len(df_kua.columns) > 9:
            col_status = df_kua.columns[9]
        df_kua = df_kua.dropna(subset=[col_item])
        df_kua = df_kua[df_kua[col_item].astype(str).str.strip() != '']
        df_kua = df_kua.rename(columns={col_item:'Dokumen'})
        if col_status:
            df_kua = df_kua.rename(columns={col_status:'Status'})
            df_kua['Done'] = df_kua['Status'].apply(clean_bool)
    else:
        df_kua = pd.DataFrame(columns=['Dokumen','Status','Done'])

    # ── TAMU — 3 grup kolom ───────────────────────────────────────────────
    raw_tamu = load_sheet_raw(SHEET_ID, GIDS["Tamu"])
    # Info sesi (row 1-3)
    info_tamu = raw_tamu[0:5] if len(raw_tamu) >= 5 else []
    # Header di row 5 (index 5), data mulai row 6 (index 6)
    tamu_header = raw_tamu[5] if len(raw_tamu) > 5 else []

    def slice_tamu(raw, col_start, col_end, header_row=5, data_start=6):
        if not raw or len(raw) <= data_start: return pd.DataFrame()
        cols_all = raw[header_row] if len(raw) > header_row else []
        sliced_headers = cols_all[col_start:col_end]
        sliced_headers = [str(c).strip() or f'col_{i}' for i,c in enumerate(sliced_headers)]
        rows = []
        for r in raw[data_start:]:
            sliced = r[col_start:col_end]
            sliced += [''] * (len(sliced_headers) - len(sliced))
            rows.append(sliced[:len(sliced_headers)])
        df = pd.DataFrame(rows, columns=sliced_headers)
        df.replace('', pd.NA, inplace=True)
        return df

    # CPW: kolom 0–8 (A–I)
    df_cpw = slice_tamu(raw_tamu, 0, 9)
    col_nama_cpw = 'Nama' if 'Nama' in df_cpw.columns else df_cpw.columns[1] if len(df_cpw.columns) > 1 else df_cpw.columns[0]
    df_cpw = df_cpw.dropna(subset=[col_nama_cpw])
    df_cpw = df_cpw[df_cpw[col_nama_cpw].astype(str).str.strip() != '']
    df_cpw = df_cpw.rename(columns={col_nama_cpw:'Nama'})
    if 'Instansi' not in df_cpw.columns and len(df_cpw.columns) > 2: df_cpw = df_cpw.rename(columns={df_cpw.columns[2]:'Instansi'})

    # CPP: kolom 10–18 (K–S)
    df_cpp = slice_tamu(raw_tamu, 10, 19)
    col_nama_cpp = 'Nama' if 'Nama' in df_cpp.columns else df_cpp.columns[1] if len(df_cpp.columns) > 1 else df_cpp.columns[0]
    df_cpp = df_cpp.dropna(subset=[col_nama_cpp])
    df_cpp = df_cpp[df_cpp[col_nama_cpp].astype(str).str.strip() != '']
    df_cpp = df_cpp.rename(columns={col_nama_cpp:'Nama'})
    if 'Instansi' not in df_cpp.columns and len(df_cpp.columns) > 2: df_cpp = df_cpp.rename(columns={df_cpp.columns[2]:'Instansi'})

    # Tamu Tanpa Undangan: kolom 20–25 (U–Z)
    df_no_inv = slice_tamu(raw_tamu, 20, 26)
    col_nama_ni = df_no_inv.columns[1] if len(df_no_inv.columns) > 1 else df_no_inv.columns[0]
    df_no_inv = df_no_inv.dropna(subset=[col_nama_ni])
    df_no_inv = df_no_inv[df_no_inv[col_nama_ni].astype(str).str.strip() != '']
    df_no_inv = df_no_inv.rename(columns={col_nama_ni:'Nama'})

    df_all_tamu = pd.concat([
        df_cpw.assign(Side='CPW (Wanita)'),
        df_cpp.assign(Side='CPP (Pria)'),
    ], ignore_index=True)

    # ── PLAYLIST ──────────────────────────────────────────────────────────
    raw_playlist = load_sheet_raw(SHEET_ID, GIDS["Playlist"])
    df_playlist = rows_to_df(raw_playlist, header_row=11, data_start=12)
    if len(df_playlist.columns) >= 2:
        col_lagu = df_playlist.columns[1]
        df_playlist = df_playlist.dropna(subset=[col_lagu])
        df_playlist = df_playlist[df_playlist[col_lagu].astype(str).str.strip().str.match(r'\w+')]

except Exception as e:
    err = str(e)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center;padding:20px 0 10px;'>
    <div style='font-size:2em;'>💍</div>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.3em;color:#f0e4d4;letter-spacing:0.05em;'>
        42272</div>
    <div style='font-size:0.7em;color:#c9a98a;letter-spacing:0.15em;text-transform:uppercase;margin-top:4px;'>
        24 Desember 2028</div>
</div>
<hr style='border-color:#6b4c3b;margin:8px 0 18px;'>
""", unsafe_allow_html=True)

pages = {
    "🏠 Overview":            "overview",
    "💰 Budget Pernikahan":   "budget",
    "💍 Budget Engagement":   "engagement",
    "🎁 Seserahan":           "seserahan",
    "💎 Mahar":               "mahar",
    "🌸 Hias Seserahan":      "hias",
    "📋 To-Do & Dokumen":     "todo",
    "👥 Tamu Undangan":       "tamu",
    "🎵 Playlist Wedding":    "playlist",
}
menu = st.sidebar.radio("Halaman", list(pages.keys()), label_visibility="collapsed")
page = pages[menu]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear(); st.rerun()
st.sidebar.markdown(f"""
<div style='text-align:center;font-size:0.62em;color:#8b6f5c;padding-top:16px;'>
    Auto-refresh tiap 6 jam<br>
    <span style='color:#c9956b;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</span>
</div>""", unsafe_allow_html=True)

# ── ERROR ─────────────────────────────────────────────────────────────────────
if err:
    st.error(f"⚠️ Gagal membaca data: {err}")
    st.info("Pastikan Service Account sudah di-share ke spreadsheet dan semua Secrets sudah diisi.")
    st.stop()

# ── HELPER UI ─────────────────────────────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(f'<h1 style="text-align:center;margin-bottom:0;">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sec-orn">{subtitle}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)

def checklist_table(df, name_col, done_col, extra_cols=None):
    display = df[[name_col]].copy()
    if extra_cols:
        for c in extra_cols:
            if c in df.columns: display[c] = df[c]
    display['Status'] = df[done_col].map({True:'✅ Selesai', False:'⏳ Belum'})
    st.dataframe(display, use_container_width=True, hide_index=True)

def plotly_defaults():
    return dict(font_family="Jost", paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_family="Cormorant Garamond", title_font_size=20)

# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "overview":
    st.markdown("""
    <div style='text-align:center;padding:20px 0 6px;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:3em;color:#2c1810;line-height:1.1;'>
            42272</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:1em;color:#8b6f5c;
             letter-spacing:0.3em;text-transform:uppercase;margin-top:4px;'>
            Wedding Command Center</div>
        <div style='color:#c9956b;font-size:1.3em;letter-spacing:0.4em;margin:6px 0;'>✦ ✦ ✦</div>
    </div>""", unsafe_allow_html=True)

    # Countdown
    d_tot, yrs, mos, d_left = get_countdown()
    if d_tot is not None:
        st.markdown(f"""
        <div style='text-align:center;font-size:0.72em;letter-spacing:0.2em;text-transform:uppercase;color:#8b6f5c;margin-bottom:10px;'>
            Menuju Hari Bahagia — 24 Desember 2028</div>
        <div class="countdown-container">
            <div class="countdown-box"><span class="cd-num">{d_tot}</span><span class="cd-lbl">Total Hari</span></div>
            <div class="countdown-box"><span class="cd-num">{yrs}</span><span class="cd-lbl">Tahun</span></div>
            <div class="countdown-box"><span class="cd-num">{mos}</span><span class="cd-lbl">Bulan</span></div>
            <div class="countdown-box"><span class="cd-num">{d_left}</span><span class="cd-lbl">Hari</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Budget summary ──
    st.markdown('<div class="sec-title">Anggaran</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)
    total_b = df_budget['Actual_Num'].sum()
    paid_b  = df_budget['Paid_Num'].sum()
    sisa_b  = df_budget['Sisa_Num'].sum()
    b1,b2,b3 = st.columns(3)
    b1.metric("Total Biaya",   fmt_rp(total_b))
    b2.metric("Sudah Dibayar", fmt_rp(paid_b))
    b3.metric("Sisa Utang",    fmt_rp(sisa_b))
    pv = paid_b/total_b if total_b>0 else 0
    st.markdown(progress_bar_html(pv*100, "Progres Pelunasan Vendor"), unsafe_allow_html=True)

    # ── Tamu summary ──
    st.markdown('<div class="sec-title">Tamu Undangan</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("👩 CPW",    f"{len(df_cpw):,} orang")
    c2.metric("👨 CPP",    f"{len(df_cpp):,} orang")
    c3.metric("👥 Total",  f"{len(df_all_tamu):,} orang")

    # ── Persiapan summary ──
    st.markdown('<div class="sec-title">Persiapan</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)

    done_ses  = df_seserahan['DONE'].sum() if 'DONE' in df_seserahan.columns else 0
    total_ses = len(df_seserahan)
    done_mhr  = df_mahar['DONE'].sum() if 'DONE' in df_mahar.columns else 0
    total_mhr = len(df_mahar)
    done_hias = df_hias['DONE'].sum() if 'DONE' in df_hias.columns else 0
    total_hias= len(df_hias)
    done_kua  = df_kua['Done'].sum() if 'Done' in df_kua.columns else 0
    total_kua = len(df_kua)

    p1,p2,p3,p4 = st.columns(4)
    p1.metric("🎁 Seserahan",  f"{int(done_ses)}/{total_ses}")
    p2.metric("💎 Mahar",      f"{int(done_mhr)}/{total_mhr}")
    p3.metric("🌸 Hias",       f"{int(done_hias)}/{total_hias}")
    p4.metric("📄 KUA Docs",   f"{int(done_kua)}/{total_kua}")

    for label, done, total in [
        ("Seserahan",       done_ses,  total_ses),
        ("Mahar",           done_mhr,  total_mhr),
        ("Hias Seserahan",  done_hias, total_hias),
        ("Dokumen KUA",     done_kua,  total_kua),
    ]:
        pct = (done/total*100) if total>0 else 0
        st.markdown(progress_bar_html(pct, label), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BUDGET PERNIKAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "budget":
    page_header("💰 Budget Pernikahan")

    total_b = df_budget['Actual_Num'].sum()
    paid_b  = df_budget['Paid_Num'].sum()
    sisa_b  = df_budget['Sisa_Num'].sum()
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Biaya",   fmt_rp(total_b))
    c2.metric("Sudah Dibayar", fmt_rp(paid_b))
    c3.metric("Sisa Utang",    fmt_rp(sisa_b))
    st.markdown(progress_bar_html((paid_b/total_b*100) if total_b>0 else 0, "Progres Pelunasan"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl,cr = st.columns(2)

    with cl:
        df_pie = df_budget[df_budget['Actual_Num']>0].copy()
        fig = px.pie(df_pie, values='Actual_Num', names='Detail',
                     title="Distribusi Biaya", hole=0.42,
                     color_discrete_sequence=px.colors.sequential.Oryel)
        fig.update_layout(**plotly_defaults())
        st.plotly_chart(fig, use_container_width=True)

    with cr:
        df_bar = df_budget[df_budget['Actual_Num']>0].copy()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='Sudah Dibayar', x=df_bar['Detail'], y=df_bar['Paid_Num'], marker_color='#8b4513'))
        fig2.add_trace(go.Bar(name='Sisa Bayar',    x=df_bar['Detail'], y=df_bar['Sisa_Num'], marker_color='#e8d5c0'))
        fig2.update_layout(barmode='stack', title='Status Pelunasan',
                           xaxis=dict(tickangle=-30), legend=dict(orientation='h',y=-0.3),
                           **plotly_defaults())
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📋 Detail Vendor")
    show_cols = [c for c in ['No','Detail','Vendor','QTY','Actual','Sudah Dibayarkan','Sisa Pembayaran','Keterangan','Payment'] if c in df_budget.columns]
    st.dataframe(df_budget[show_cols], use_container_width=True, hide_index=True)

    # Payment timeline jika ada tanggal
    if 'Tanggal Pelunasan' in df_budget.columns:
        st.markdown("#### 🗓️ Info Tanggal Pembayaran")
        df_dates = df_budget[['Detail','Tanggal DP','Tanggal Pelunasan','Keterangan']].dropna(subset=['Tanggal Pelunasan'])
        if not df_dates.empty:
            st.dataframe(df_dates, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# BUDGET ENGAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "engagement":
    page_header("💍 Budget Engagement Day")

    if df_engagement.empty:
        st.info("Data engagement belum tersedia atau GID belum dikonfigurasi.")
    else:
        total_e  = df_engagement['Budget_Num'].sum()
        actual_e = df_engagement['Actual_Num'].sum()
        sisa_e   = actual_e - total_e

        c1,c2,c3 = st.columns(3)
        c1.metric("Budget",    fmt_rp(total_e))
        c2.metric("Actual",    fmt_rp(actual_e))
        c3.metric("Selisih",   fmt_rp(sisa_e))

        st.markdown("<br>", unsafe_allow_html=True)

        if 'STATUS' in df_engagement.columns:
            paid_e = df_engagement[df_engagement['STATUS'].astype(str).str.upper()=='PAID']['Actual_Num'].sum()
            st.markdown(progress_bar_html((paid_e/actual_e*100) if actual_e>0 else 0, "Sudah Terbayar"), unsafe_allow_html=True)

        show_cols = [c for c in ['NO','ITEM','BRAND','BUDGET','ACTUAL','DISCOUNT','STATUS','STORE/LINK'] if c in df_engagement.columns]
        st.dataframe(df_engagement[show_cols], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESERAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "seserahan":
    page_header("🎁 Seserahan")

    done_ses  = int(df_seserahan['DONE'].sum()) if 'DONE' in df_seserahan.columns else 0
    total_ses = len(df_seserahan)
    m1,m2,m3 = st.columns(3)
    m1.metric("Total Item",  f"{total_ses}")
    m2.metric("✅ Siap",     f"{done_ses}")
    m3.metric("⏳ Belum",    f"{total_ses-done_ses}")
    st.markdown(progress_bar_html((done_ses/total_ses*100) if total_ses>0 else 0, "Progress Seserahan"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter
    col_f, col_s = st.columns([1,3])
    with col_f:
        flt = st.radio("Filter:", ["Semua","Belum","Siap"], horizontal=True, key="ses_flt")
    with col_s:
        q = st.text_input("Cari item...", label_visibility="collapsed", placeholder="Cari nama item seserahan...")

    df_s = df_seserahan.copy()
    if flt == "Belum": df_s = df_s[df_s['DONE']==False]
    elif flt == "Siap": df_s = df_s[df_s['DONE']==True]
    if q: df_s = df_s[df_s['LIST SESERAHAN'].astype(str).str.lower().str.contains(q.lower(),na=False)|
                      df_s['DETAIL'].astype(str).str.lower().str.contains(q.lower(),na=False) if 'DETAIL' in df_s.columns else df_s['LIST SESERAHAN'].astype(str).str.lower().str.contains(q.lower(),na=False)]

    df_s['Status'] = df_s['DONE'].map({True:'✅ Siap',False:'⏳ Belum'})
    show = [c for c in ['LIST SESERAHAN','DETAIL','BRAND','MODEL','NORMAL PRICE','FINAL PRICE','STORE/LINK','Status'] if c in df_s.columns]
    st.dataframe(df_s[show], use_container_width=True, hide_index=True)

    if 'FINAL PRICE' in df_seserahan.columns:
        total_ses_rp = df_seserahan['Final_Num'].sum()
        budget_ses   = 3000000
        st.markdown(f"""
        <div class="info-box" style="margin-top:16px;">
            <b>💰 Estimasi Total Biaya Seserahan:</b> {fmt_rp(total_ses_rp)}<br>
            <b>📊 Budget:</b> {fmt_rp(budget_ses)}<br>
            <b>{'✅ On budget' if total_ses_rp<=budget_ses else '⚠️ Over budget'}</b>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAHAR
# ─────────────────────────────────────────────────────────────────────────────
elif page == "mahar":
    page_header("💎 Mahar")

    if df_mahar.empty:
        st.info("Data mahar belum diisi di spreadsheet.")
    else:
        done_m  = int(df_mahar['DONE'].sum())
        total_m = len(df_mahar)
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Item",f"{total_m}")
        m2.metric("✅ Siap",   f"{done_m}")
        m3.metric("⏳ Belum",  f"{total_m-done_m}")
        st.markdown(progress_bar_html((done_m/total_m*100) if total_m>0 else 0,"Progress Mahar"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        df_mahar['Status'] = df_mahar['DONE'].map({True:'✅ Siap',False:'⏳ Belum'})
        show = [c for c in ['LIST MAHAR','BRAND','ESTIMASI','FINAL PRICE','Status'] if c in df_mahar.columns]
        st.dataframe(df_mahar[show], use_container_width=True, hide_index=True)

        total_est   = df_mahar['Est_Num'].sum() if 'Est_Num' in df_mahar.columns else 0
        total_final = df_mahar['Final_Num'].sum() if 'Final_Num' in df_mahar.columns else 0
        if total_est > 0 or total_final > 0:
            st.markdown(f"""
            <div class="info-box" style="margin-top:16px;">
                <b>💰 Estimasi Total Mahar:</b> {fmt_rp(total_est)}<br>
                <b>💰 Final Total Mahar:</b> {fmt_rp(total_final)}
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HIAS SESERAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "hias":
    page_header("🌸 Hias Seserahan & Mahar")

    if df_hias.empty:
        st.info("Data hias seserahan belum diisi.")
    else:
        done_h  = int(df_hias['DONE'].sum())
        total_h = len(df_hias)
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Item",f"{total_h}")
        m2.metric("✅ Siap",   f"{done_h}")
        m3.metric("⏳ Belum",  f"{total_h-done_h}")
        st.markdown(progress_bar_html((done_h/total_h*100) if total_h>0 else 0,"Progress Hias"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        df_hias['Status'] = df_hias['DONE'].map({True:'✅ Siap',False:'⏳ Belum'})
        show = [c for c in ['LIST','BRAND','ESTIMASI','FINAL PRICE','Status'] if c in df_hias.columns]
        st.dataframe(df_hias[show], use_container_width=True, hide_index=True)

        total_est_h = df_hias['Est_Num'].sum() if 'Est_Num' in df_hias.columns else 0
        if total_est_h > 0:
            st.markdown(f'<div class="info-box"><b>💰 Estimasi Total:</b> {fmt_rp(total_est_h)}</div>',
                        unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TO-DO & DOKUMEN KUA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "todo":
    page_header("📋 To-Do & Dokumen KUA")

    tab1, tab2 = st.tabs(["📌 To-Do Tasks", "📄 Dokumen KUA"])

    with tab1:
        st.markdown("#### Daftar Kegiatan Persiapan")
        if df_tasks.empty:
            st.info("Data tasks belum tersedia.")
        else:
            done_dp = df_tasks['DP_Done'].sum() if 'DP_Done' in df_tasks.columns else 0
            done_fp = df_tasks['FP_Done'].sum() if 'FP_Done' in df_tasks.columns else 0
            total_t = len(df_tasks)

            c1,c2,c3 = st.columns(3)
            c1.metric("Total Kegiatan", f"{total_t}")
            c2.metric("💰 DP Selesai",  f"{int(done_dp)}")
            c3.metric("✅ Lunas",        f"{int(done_fp)}")
            st.markdown(progress_bar_html((done_fp/total_t*100) if total_t>0 else 0, "Progress Pelunasan Tasks"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            show = ['No','Kegiatan']
            if 'DP_Done' in df_tasks.columns:
                df_tasks['DP Status'] = df_tasks['DP_Done'].map({True:'✅',False:'⏳'})
                show.append('DP Status')
            if 'FP_Done' in df_tasks.columns:
                df_tasks['Lunas'] = df_tasks['FP_Done'].map({True:'✅',False:'⏳'})
                show.append('Lunas')
            st.dataframe(df_tasks[[c for c in show if c in df_tasks.columns]], use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### Dokumen Persyaratan KUA")
        if df_kua.empty:
            st.info("Data dokumen KUA belum tersedia.")
        else:
            done_kua  = int(df_kua['Done'].sum()) if 'Done' in df_kua.columns else 0
            total_kua = len(df_kua)
            k1,k2,k3 = st.columns(3)
            k1.metric("Total Dokumen", f"{total_kua}")
            k2.metric("✅ Selesai",    f"{done_kua}")
            k3.metric("⏳ Belum",      f"{total_kua-done_kua}")
            st.markdown(progress_bar_html((done_kua/total_kua*100) if total_kua>0 else 0, "Kelengkapan Dokumen"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            df_kua_show = df_kua.copy()
            if 'Done' in df_kua_show.columns:
                df_kua_show['Status Display'] = df_kua_show['Done'].map({True:'✅ Selesai',False:'⏳ Belum'})
            show = [c for c in ['Dokumen','Status Display'] if c in df_kua_show.columns]
            if not show: show = df_kua_show.columns[:2].tolist()
            st.dataframe(df_kua_show[show], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAMU UNDANGAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "tamu":
    page_header("👥 Tamu Undangan")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("👩 CPW",          f"{len(df_cpw):,}")
    c2.metric("👨 CPP",          f"{len(df_cpp):,}")
    c3.metric("👥 Total Diundang",f"{len(df_all_tamu):,}")
    c4.metric("📋 Tanpa Undangan",f"{len(df_no_inv):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Semua Tamu", "👩 CPW", "👨 CPP"])

    def tamu_tab_content(df, label):
        q_col, f_col = st.columns([3,1])
        with q_col:
            q = st.text_input("Cari...", placeholder=f"Cari tamu {label}...", label_visibility="collapsed", key=f"q_{label}")
        with f_col:
            inst_list = ["Semua"] + sorted(df['Instansi'].dropna().unique().tolist()) if 'Instansi' in df.columns else ["Semua"]
            inst_filter = st.selectbox("Instansi", inst_list, label_visibility="collapsed", key=f"inst_{label}")

        df_f = df.copy()
        if q:
            mask = df_f['Nama'].astype(str).str.lower().str.contains(q.lower(),na=False)
            if 'Instansi' in df_f.columns:
                mask |= df_f['Instansi'].astype(str).str.lower().str.contains(q.lower(),na=False)
            df_f = df_f[mask]
        if inst_filter != "Semua" and 'Instansi' in df_f.columns:
            df_f = df_f[df_f['Instansi'].astype(str)==inst_filter]

        st.markdown(f"<div style='font-size:0.82em;color:#8b6f5c;margin-bottom:6px;'>Menampilkan {len(df_f)} tamu</div>", unsafe_allow_html=True)
        show = [c for c in ['Nama','Instansi','Ket'] if c in df_f.columns]
        if 'Side' in df_f.columns: show.append('Side')
        st.dataframe(df_f[show], use_container_width=True, hide_index=True, height=400)

        # Breakdown instansi
        if 'Instansi' in df_f.columns and len(df_f) > 0:
            ic = df_f['Instansi'].dropna().value_counts().head(10).reset_index()
            ic.columns = ['Instansi','Jumlah']
            if not ic.empty:
                fig = px.bar(ic, x='Jumlah', y='Instansi', orientation='h',
                             title=f'Top Instansi — {label}', color='Jumlah',
                             color_continuous_scale='Oryel')
                fig.update_layout(**plotly_defaults(), yaxis=dict(autorange="reversed"),
                                  coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab1:
        tamu_tab_content(df_all_tamu, "semua")

    with tab2:
        tamu_tab_content(df_cpw, "CPW")

    with tab3:
        tamu_tab_content(df_cpp, "CPP")

    # Tamu tanpa undangan (bonus)
    if not df_no_inv.empty:
        with st.expander(f"📋 Tamu Tanpa Undangan ({len(df_no_inv)} orang)"):
            show_ni = [c for c in df_no_inv.columns if not str(c).startswith('col_')][:4]
            st.dataframe(df_no_inv[show_ni], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLAYLIST
# ─────────────────────────────────────────────────────────────────────────────
elif page == "playlist":
    page_header("🎵 Playlist Wedding")

    # Info vendor (baris 4-9 di sheet)
    st.markdown("""
    <div class="info-box">
        <b>🎤 Vendor Entertainment</b><br>
        Isi detail vendor di spreadsheet tab <i>Playlist Wedding</i> (baris Format Instrumen, Jam Standby, Jam Acara, Entrance, dll.)
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🎶 Request Lagu")

    if df_playlist.empty:
        st.info("Belum ada lagu yang dimasukkan. Tambahkan di tab Playlist Wedding di spreadsheet.")
    else:
        q = st.text_input("Cari lagu atau penyanyi...", label_visibility="collapsed",
                          placeholder="Ketik judul atau penyanyi...")
        df_pl = df_playlist.copy()
        if q:
            col_lagu = df_pl.columns[1] if len(df_pl.columns)>1 else df_pl.columns[0]
            col_art  = df_pl.columns[2] if len(df_pl.columns)>2 else col_lagu
            df_pl = df_pl[
                df_pl[col_lagu].astype(str).str.lower().str.contains(q.lower(),na=False)|
                df_pl[col_art].astype(str).str.lower().str.contains(q.lower(),na=False)
            ]
        show_pl = [c for c in df_pl.columns if not str(c).startswith('Unnamed')][:5]
        st.dataframe(df_pl[show_pl], use_container_width=True, hide_index=True)
        st.markdown(f"<div style='font-size:0.82em;color:#8b6f5c;'>Total {len(df_pl)} lagu</div>", unsafe_allow_html=True)

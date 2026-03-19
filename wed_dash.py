import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import traceback

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
p, span, div, li, td, th,
[data-testid="stMarkdownContainer"] * { color: #2c1810 !important; }
h1,h2,h3,h4 { font-family:'Cormorant Garamond',serif !important; color:#2c1810 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#2c1810 0%,#4a2c20 100%) !important; }
[data-testid="stSidebar"] * { color:#f0e4d4 !important; }
[data-testid="metric-container"] {
    background:rgba(255,255,255,0.85) !important;
    border:1px solid #e8d5c0 !important; border-radius:12px; padding:16px;
}
[data-testid="metric-container"] label {
    font-size:0.72em !important; text-transform:uppercase;
    letter-spacing:0.08em; color:#8b6f5c !important;
}
[data-testid="stMetricValue"] {
    font-family:'Cormorant Garamond',serif !important;
    font-size:1.7em !important; color:#2c1810 !important;
}
[data-testid="stDataFrame"] { border:1px solid #e8d5c0; border-radius:12px; overflow:hidden; }
.stButton>button {
    background:linear-gradient(135deg,#2c1810,#4a2c20) !important;
    color:#f0e4d4 !important; border:none; border-radius:8px;
    font-family:'Jost',sans-serif; letter-spacing:0.1em;
    text-transform:uppercase; font-size:0.78em; padding:0.5em 1.5em;
}
.stProgress>div>div { background:linear-gradient(90deg,#c9956b,#8b4513) !important; }
.stTabs [data-baseweb="tab"] {
    background:rgba(255,255,255,0.55); border:1px solid #e8d5c0;
    border-radius:8px; color:#8b6f5c !important; font-family:'Jost',sans-serif;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#2c1810,#4a2c20) !important;
    color:#f0e4d4 !important;
}
.stTextInput input,.stSelectbox>div {
    background:rgba(255,255,255,0.9) !important;
    color:#2c1810 !important; border:1px solid #e8d5c0 !important; border-radius:8px;
}
.stRadio label { color:#2c1810 !important; }
hr { border-color:#e8d5c0; }
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
        "Start":     st.secrets["GID_START"],
        "Budget":    st.secrets["GID_BUDGET"],
        "Budgeting": st.secrets["GID_BUDGETING"],
        "Seserahan": st.secrets["GID_SESERAHAN"],
        "Todo":      st.secrets["GID_TODO"],
        "Tamu":      st.secrets["GID_TAMU"],
        "Playlist":  st.secrets["GID_PLAYLIST"],
    }
except Exception:
    SHEET_ID = "1vfMBjDcu5vqbcKLAWGriDA89S3bbjkUH8mSU3GLrEs0"
    GIDS = {
        "Start":     "180476786",
        "Budget":    "771919678",
        "Budgeting": "0",
        "Seserahan": "1333161294",
        "Todo":      "39054956",
        "Tamu":      "1724463210",
        "Playlist":  "608864392",
    }

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
    try:
        client = get_gspread_client()
        ws = next((w for w in client.open_by_key(sheet_id).worksheets()
                   if str(w.id) == str(gid)), None)
        if ws is None:
            return []
        return ws.get_all_values()
    except Exception:
        return []

def rows_to_df(all_rows: list, header_row: int, data_start: int, data_end: int = None) -> pd.DataFrame:
    if not all_rows or header_row >= len(all_rows):
        return pd.DataFrame()
    raw_headers = [str(c).strip() for c in all_rows[header_row]]
    seen = {}
    headers = []
    for h in raw_headers:
        if h == '' or h in seen:
            base = h if h != '' else 'col'
            seen[base] = seen.get(base, 0) + 1
            headers.append(f"{base}_{seen[base]}")
        else:
            seen[h] = 0
            headers.append(h)
    end = data_end if data_end is not None else len(all_rows)
    rows = all_rows[data_start:end]
    processed = []
    for r in rows:
        row = list(r)
        if len(row) < len(headers):
            row += [''] * (len(headers) - len(row))
        row = row[:len(headers)]
        processed.append(row)
    if not processed:
        return pd.DataFrame(columns=headers)
    df = pd.DataFrame(processed, columns=headers)
    for col in df.columns:
        df[col] = df[col].apply(lambda x: pd.NA if (x == '' or x is None) else x)
    return df

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clean_currency(val) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    s = str(val).strip()
    if s == '' or s.upper() in ['NA', 'NAN', 'NONE', '-']:
        return 0.0
    s = s.replace('Rp','').replace('rp','').replace('.','').replace(',','').strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def clean_bool(val) -> bool:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    s = str(val).strip().upper()
    return s in ['TRUE','CHECKED','1','1.0','V','YA','YES','✓','SELESAI','DONE']

def fmt_rp(v: float) -> str:
    return f"Rp {v:,.0f}"

def get_countdown():
    d = (WEDDING_DATE - date.today()).days
    if d < 0:
        return None, None, None, None
    return d, d // 365, (d % 365) // 30, (d % 365) % 30

def progress_bar_html(pct: float, label: str = "") -> str:
    pct = max(0.0, min(100.0, float(pct)))
    color = "#8b4513" if pct < 50 else "#c9956b" if pct < 80 else "#2d7a2d"
    return f"""<div style='margin:6px 0 14px;'>
        <div style='display:flex;justify-content:space-between;font-size:0.78em;color:#8b6f5c;margin-bottom:4px;'>
            <span>{label}</span><span>{pct:.1f}%</span>
        </div>
        <div style='background:#e8d5c0;border-radius:8px;height:10px;'>
            <div style='background:{color};width:{pct:.1f}%;height:10px;border-radius:8px;'></div>
        </div>
    </div>"""

def col_as_series(df: pd.DataFrame, col: str) -> pd.Series:
    """Return kolom sebagai Series string. Aman untuk .str operations."""
    if col not in df.columns:
        return pd.Series([''] * len(df), dtype=str)
    return df[col].fillna('').astype(str)

def safe_sum(df: pd.DataFrame, col: str) -> int:
    """Sum boolean/numeric kolom dengan aman."""
    if df is None or df.empty or col not in df.columns:
        return 0
    return int(df[col].sum())

def search_filter_df(df: pd.DataFrame, search_cols: list, query: str) -> pd.DataFrame:
    """Filter DataFrame multi-kolom. Aman dari semua edge case."""
    if df is None or df.empty or not query or not search_cols:
        return df if df is not None else pd.DataFrame()
    q = query.lower().strip()
    mask = pd.Series([False] * len(df), index=df.index)
    for col in search_cols:
        if col in df.columns:
            mask = mask | col_as_series(df, col).str.lower().str.contains(q, na=False, regex=False)
    return df[mask]

def empty_df(*cols) -> pd.DataFrame:
    """Buat DataFrame kosong dengan kolom tertentu."""
    return pd.DataFrame(columns=list(cols))

# ── FIX UTAMA: safe_load yang benar ──────────────────────────────────────────
# SALAH:  result = safe_load(...) or pd.DataFrame(...)
#         → Python evaluasi "DataFrame or X" → ValueError karena ambigu
#
# BENAR:  result = safe_load(...)
#         if result is None: result = pd.DataFrame(...)
#
# Solusinya: safe_load sekarang selalu return tuple (result, error_msg)
# sehingga kita cek `result is None` bukan evaluasi boolean DataFrame.

load_errors = []

def safe_load(name: str, fn):
    """
    Panggil fn() dengan error handling.
    Return: hasil fn() kalau sukses, atau None kalau error.
    Error disimpan ke load_errors untuk ditampilkan di UI.
    """
    try:
        return fn()
    except Exception as e:
        load_errors.append(f"[{name}] {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return None

# ── LOAD: BUDGET ──────────────────────────────────────────────────────────────
def load_budget():
    raw = load_sheet_raw(SHEET_ID, GIDS["Budget"])
    df = rows_to_df(raw, header_row=2, data_start=3, data_end=30)
    if df.empty or 'Detail' not in df.columns:
        return empty_df('Detail','Actual_Num','Paid_Num','Sisa_Num')
    df = df[col_as_series(df, 'Detail').str.strip() != ''].copy()
    df = df.dropna(subset=['Detail'])
    df['Actual_Num'] = df['Actual'].apply(clean_currency) if 'Actual' in df.columns else 0.0
    df['Paid_Num']   = df['Sudah Dibayarkan'].apply(clean_currency) if 'Sudah Dibayarkan' in df.columns else 0.0
    df['Sisa_Num']   = df['Actual_Num'] - df['Paid_Num']
    return df

_r = safe_load("Budget", load_budget)
df_budget = _r if _r is not None else empty_df('Detail','Actual_Num','Paid_Num','Sisa_Num')

# ── LOAD: ENGAGEMENT ──────────────────────────────────────────────────────────
def load_engagement():
    raw = load_sheet_raw(SHEET_ID, GIDS["Budgeting"])
    if not raw:
        return empty_df()
    df = rows_to_df(raw, header_row=9, data_start=10, data_end=35)
    if df.empty:
        return empty_df()
    item_col = next((c for c in ['ITEM','Item','item'] if c in df.columns), None)
    if item_col is None:
        return empty_df()
    df = df[col_as_series(df, item_col).str.strip() != ''].copy()
    df = df.dropna(subset=[item_col])
    df['Budget_Num'] = df['BUDGET'].apply(clean_currency) if 'BUDGET' in df.columns else 0.0
    df['Actual_Num'] = df['ACTUAL'].apply(clean_currency) if 'ACTUAL' in df.columns else 0.0
    return df

_r = safe_load("Engagement", load_engagement)
df_engagement = _r if _r is not None else empty_df()

# ── LOAD: SESERAHAN (3 tabel) ─────────────────────────────────────────────────
def load_seserahan():
    raw = load_sheet_raw(SHEET_ID, GIDS["Seserahan"])
    if not raw:
        return empty_df('LIST SESERAHAN','DONE'), empty_df('LIST MAHAR','DONE'), empty_df('LIST','DONE')

    # Tabel 1: Seserahan (header=2, data=3–35)
    df_ses = rows_to_df(raw, header_row=2, data_start=3, data_end=36)
    if 'LIST SESERAHAN' in df_ses.columns:
        df_ses = df_ses[col_as_series(df_ses,'LIST SESERAHAN').str.strip() != ''].copy()
        df_ses = df_ses.dropna(subset=['LIST SESERAHAN'])
        df_ses['DONE']       = df_ses['CHECKLIST'].apply(clean_bool) if 'CHECKLIST' in df_ses.columns else False
        df_ses['Normal_Num'] = df_ses['NORMAL PRICE'].apply(clean_currency) if 'NORMAL PRICE' in df_ses.columns else 0.0
        df_ses['Final_Num']  = df_ses['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_ses.columns else 0.0
    else:
        df_ses = empty_df('LIST SESERAHAN','DONE')

    # Tabel 2: Mahar (header=40, data=41–46)
    df_mhr = rows_to_df(raw, header_row=40, data_start=41, data_end=47)
    if 'LIST MAHAR' in df_mhr.columns:
        df_mhr = df_mhr[col_as_series(df_mhr,'LIST MAHAR').str.strip() != ''].copy()
        df_mhr = df_mhr.dropna(subset=['LIST MAHAR'])
        df_mhr['DONE']      = df_mhr['CHECKLIST'].apply(clean_bool) if 'CHECKLIST' in df_mhr.columns else False
        df_mhr['Est_Num']   = df_mhr['ESTIMASI'].apply(clean_currency) if 'ESTIMASI' in df_mhr.columns else 0.0
        df_mhr['Final_Num'] = df_mhr['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_mhr.columns else 0.0
    else:
        df_mhr = empty_df('LIST MAHAR','DONE')

    # Tabel 3: Hias Seserahan (header=48, data=49–58)
    df_hias = rows_to_df(raw, header_row=48, data_start=49, data_end=59)
    if 'LIST' in df_hias.columns:
        df_hias = df_hias[col_as_series(df_hias,'LIST').str.strip() != ''].copy()
        df_hias = df_hias.dropna(subset=['LIST'])
        chk = 'CHECKLIS' if 'CHECKLIS' in df_hias.columns else ('CHECKLIST' if 'CHECKLIST' in df_hias.columns else None)
        df_hias['DONE']      = df_hias[chk].apply(clean_bool) if chk else False
        df_hias['Est_Num']   = df_hias['ESTIMASI'].apply(clean_currency) if 'ESTIMASI' in df_hias.columns else 0.0
        df_hias['Final_Num'] = df_hias['FINAL PRICE'].apply(clean_currency) if 'FINAL PRICE' in df_hias.columns else 0.0
    else:
        df_hias = empty_df('LIST','DONE')

    return df_ses, df_mhr, df_hias

_r = safe_load("Seserahan", load_seserahan)
if _r is not None and len(_r) == 3:
    df_seserahan, df_mahar, df_hias = _r
else:
    df_seserahan = empty_df('LIST SESERAHAN','DONE')
    df_mahar     = empty_df('LIST MAHAR','DONE')
    df_hias      = empty_df('LIST','DONE')

# ── LOAD: TODO (2 tabel) ──────────────────────────────────────────────────────
def load_todo():
    raw = load_sheet_raw(SHEET_ID, GIDS["Todo"])
    if not raw:
        return empty_df('No','Kegiatan'), empty_df('Dokumen','Done')

    # Tabel 1: Tasks Gantt (header=3, data=6–27)
    df_t = rows_to_df(raw, header_row=3, data_start=6, data_end=28)
    if len(df_t.columns) >= 2:
        col_no  = df_t.columns[0]
        col_keg = df_t.columns[1]
        df_t = df_t[col_as_series(df_t, col_keg).str.strip() != ''].copy()
        df_t = df_t.dropna(subset=[col_keg])
        df_t = df_t.rename(columns={col_no:'No', col_keg:'Kegiatan'})
        if len(df_t.columns) > 37:
            df_t['DP_Done'] = df_t[df_t.columns[37]].apply(clean_bool)
        if len(df_t.columns) > 38:
            df_t['FP_Done'] = df_t[df_t.columns[38]].apply(clean_bool)
    else:
        df_t = empty_df('No','Kegiatan')

    # Tabel 2: KUA Dokumen (header=29, data=30–43)
    df_k = rows_to_df(raw, header_row=29, data_start=30, data_end=44)
    if len(df_k.columns) >= 2:
        col_doc = df_k.columns[1]
        df_k = df_k[col_as_series(df_k, col_doc).str.strip() != ''].copy()
        df_k = df_k.dropna(subset=[col_doc])
        df_k = df_k.rename(columns={col_doc:'Dokumen'})
        if len(df_k.columns) > 9:
            col_status = df_k.columns[9]
            df_k = df_k.rename(columns={col_status:'Status'})
            df_k['Done'] = df_k['Status'].apply(clean_bool)
        else:
            df_k['Done'] = False
    else:
        df_k = empty_df('Dokumen','Status','Done')

    return df_t, df_k

_r = safe_load("Todo", load_todo)
if _r is not None and len(_r) == 2:
    df_tasks, df_kua = _r
else:
    df_tasks = empty_df('No','Kegiatan')
    df_kua   = empty_df('Dokumen','Done')

# ── LOAD: TAMU (3 grup kolom) ─────────────────────────────────────────────────
def load_tamu():
    raw = load_sheet_raw(SHEET_ID, GIDS["Tamu"])
    if not raw:
        return empty_df('Nama'), empty_df('Nama'), empty_df('Nama')

    def slice_cols(raw_data, col_start, col_end, header_row=5, data_start=6):
        if len(raw_data) <= header_row:
            return pd.DataFrame()
        all_headers = raw_data[header_row] if len(raw_data) > header_row else []
        h_slice = all_headers[col_start:col_end]
        final_headers = []
        used = {}
        for i, h in enumerate(h_slice):
            h = str(h).strip()
            if h == '':
                h = f'_col{col_start + i}'
            if h in used:
                used[h] += 1
                h = f'{h}_{used[h]}'
            else:
                used[h] = 0
            final_headers.append(h)
        rows = []
        for r in raw_data[data_start:]:
            sliced = list(r[col_start:col_end])
            while len(sliced) < len(final_headers):
                sliced.append('')
            sliced = sliced[:len(final_headers)]
            rows.append(sliced)
        if not rows:
            return pd.DataFrame(columns=final_headers)
        df = pd.DataFrame(rows, columns=final_headers)
        for c in df.columns:
            df[c] = df[c].apply(lambda x: pd.NA if x == '' else x)
        return df

    def clean_tamu(df):
        if df.empty:
            return df
        nama_col = 'Nama' if 'Nama' in df.columns else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
        df = df[col_as_series(df, nama_col).str.strip() != ''].copy()
        df = df.dropna(subset=[nama_col])
        if nama_col != 'Nama':
            df = df.rename(columns={nama_col:'Nama'})
        if 'Instansi' not in df.columns and len(df.columns) > 2:
            df = df.rename(columns={df.columns[2]:'Instansi'})
        return df

    df_w  = clean_tamu(slice_cols(raw, 0, 9))
    df_p  = clean_tamu(slice_cols(raw, 10, 19))

    df_ni = slice_cols(raw, 20, 26)
    if not df_ni.empty and len(df_ni.columns) > 1:
        nama_ni = df_ni.columns[1]
        df_ni = df_ni[col_as_series(df_ni, nama_ni).str.strip() != ''].copy()
        df_ni = df_ni.dropna(subset=[nama_ni])
        df_ni = df_ni.rename(columns={nama_ni:'Nama'})

    return df_w, df_p, df_ni

_r = safe_load("Tamu", load_tamu)
if _r is not None and len(_r) == 3:
    df_cpw, df_cpp, df_no_inv = _r
else:
    df_cpw    = empty_df('Nama')
    df_cpp    = empty_df('Nama')
    df_no_inv = empty_df('Nama')

df_all_tamu = pd.concat([
    df_cpw.assign(Side='CPW (Wanita)'),
    df_cpp.assign(Side='CPP (Pria)'),
], ignore_index=True)

# ── LOAD: PLAYLIST ────────────────────────────────────────────────────────────
def load_playlist():
    raw = load_sheet_raw(SHEET_ID, GIDS["Playlist"])
    if not raw:
        return empty_df()
    df = rows_to_df(raw, header_row=11, data_start=12)
    if df.empty or len(df.columns) < 2:
        return empty_df()
    col_lagu = df.columns[1]
    mask = col_as_series(df, col_lagu).str.strip().str.len() > 0
    mask = mask & (~col_as_series(df, col_lagu).str.match(r'^\d+\.?$'))
    return df[mask].copy()

_r = safe_load("Playlist", load_playlist)
df_playlist = _r if _r is not None else empty_df()

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
    "🏠 Overview":          "overview",
    "💰 Budget Pernikahan": "budget",
    "💍 Budget Engagement": "engagement",
    "🎁 Seserahan":         "seserahan",
    "💎 Mahar":             "mahar",
    "🌸 Hias Seserahan":    "hias",
    "📋 To-Do & Dokumen":   "todo",
    "👥 Tamu Undangan":     "tamu",
    "🎵 Playlist Wedding":  "playlist",
}
menu = st.sidebar.radio("Halaman", list(pages.keys()), label_visibility="collapsed")
page = pages[menu]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(f"""
<div style='text-align:center;font-size:0.62em;color:#8b6f5c;padding-top:16px;'>
    Auto-refresh tiap 6 jam<br>
    <span style='color:#c9956b;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</span>
</div>""", unsafe_allow_html=True)

# ── TAMPILKAN ERROR ───────────────────────────────────────────────────────────
if load_errors:
    with st.expander(f"⚠️ {len(load_errors)} bagian gagal dimuat — klik untuk detail"):
        for e in load_errors:
            st.code(e)

# ── HELPER UI ─────────────────────────────────────────────────────────────────
def page_header(title, subtitle=""):
    st.markdown(f'<h1 style="text-align:center;margin-bottom:0;">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-orn">{subtitle if subtitle else "— ✦ —"}</div>', unsafe_allow_html=True)

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

    d_tot, yrs, mos, d_left = get_countdown()
    if d_tot is not None:
        st.markdown(f"""
        <div style='text-align:center;font-size:0.72em;letter-spacing:0.2em;text-transform:uppercase;
             color:#8b6f5c;margin-bottom:10px;'>Menuju Hari Bahagia — 24 Desember 2028</div>
        <div class="countdown-container">
            <div class="countdown-box"><span class="cd-num">{d_tot}</span><span class="cd-lbl">Total Hari</span></div>
            <div class="countdown-box"><span class="cd-num">{yrs}</span><span class="cd-lbl">Tahun</span></div>
            <div class="countdown-box"><span class="cd-num">{mos}</span><span class="cd-lbl">Bulan</span></div>
            <div class="countdown-box"><span class="cd-num">{d_left}</span><span class="cd-lbl">Hari</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-title">Anggaran</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)
    total_b = df_budget['Actual_Num'].sum() if 'Actual_Num' in df_budget.columns else 0
    paid_b  = df_budget['Paid_Num'].sum()   if 'Paid_Num'   in df_budget.columns else 0
    sisa_b  = df_budget['Sisa_Num'].sum()   if 'Sisa_Num'   in df_budget.columns else 0
    b1,b2,b3 = st.columns(3)
    b1.metric("Total Biaya",   fmt_rp(total_b))
    b2.metric("Sudah Dibayar", fmt_rp(paid_b))
    b3.metric("Sisa Utang",    fmt_rp(sisa_b))
    st.markdown(progress_bar_html((paid_b/total_b*100) if total_b>0 else 0, "Progres Pelunasan Vendor"), unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Tamu Undangan</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("👩 CPW",   f"{len(df_cpw):,} orang")
    c2.metric("👨 CPP",   f"{len(df_cpp):,} orang")
    c3.metric("👥 Total", f"{len(df_all_tamu):,} orang")

    st.markdown('<div class="sec-title">Persiapan</div><div class="sec-orn">— ✦ —</div>', unsafe_allow_html=True)
    done_ses  = safe_sum(df_seserahan,'DONE'); total_ses  = len(df_seserahan)
    done_mhr  = safe_sum(df_mahar,    'DONE'); total_mhr  = len(df_mahar)
    done_hias = safe_sum(df_hias,     'DONE'); total_hias = len(df_hias)
    done_kua  = safe_sum(df_kua,      'Done'); total_kua  = len(df_kua)
    p1,p2,p3,p4 = st.columns(4)
    p1.metric("🎁 Seserahan", f"{done_ses}/{total_ses}")
    p2.metric("💎 Mahar",     f"{done_mhr}/{total_mhr}")
    p3.metric("🌸 Hias",      f"{done_hias}/{total_hias}")
    p4.metric("📄 KUA Docs",  f"{done_kua}/{total_kua}")
    for label, done, total in [
        ("Seserahan", done_ses, total_ses), ("Mahar", done_mhr, total_mhr),
        ("Hias Seserahan", done_hias, total_hias), ("Dokumen KUA", done_kua, total_kua),
    ]:
        st.markdown(progress_bar_html((done/total*100) if total>0 else 0, label), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BUDGET PERNIKAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "budget":
    page_header("💰 Budget Pernikahan")
    total_b = df_budget['Actual_Num'].sum() if 'Actual_Num' in df_budget.columns else 0
    paid_b  = df_budget['Paid_Num'].sum()   if 'Paid_Num'   in df_budget.columns else 0
    sisa_b  = df_budget['Sisa_Num'].sum()   if 'Sisa_Num'   in df_budget.columns else 0
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Biaya",   fmt_rp(total_b))
    c2.metric("Sudah Dibayar", fmt_rp(paid_b))
    c3.metric("Sisa Utang",    fmt_rp(sisa_b))
    st.markdown(progress_bar_html((paid_b/total_b*100) if total_b>0 else 0, "Progres Pelunasan"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df_chart = df_budget[df_budget['Actual_Num']>0].copy() if 'Actual_Num' in df_budget.columns else pd.DataFrame()
    if not df_chart.empty:
        cl,cr = st.columns(2)
        with cl:
            fig = px.pie(df_chart, values='Actual_Num', names='Detail', title="Distribusi Biaya",
                         hole=0.42, color_discrete_sequence=px.colors.sequential.Oryel)
            fig.update_layout(**plotly_defaults())
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name='Sudah Dibayar', x=df_chart['Detail'], y=df_chart['Paid_Num'], marker_color='#8b4513'))
            fig2.add_trace(go.Bar(name='Sisa Bayar',    x=df_chart['Detail'], y=df_chart['Sisa_Num'], marker_color='#e8d5c0'))
            fig2.update_layout(barmode='stack', title='Status Pelunasan',
                               xaxis=dict(tickangle=-30), legend=dict(orientation='h',y=-0.3),
                               **plotly_defaults())
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📋 Detail Vendor")
    show_cols = [c for c in ['No','Detail','Vendor','QTY','Actual','Sudah Dibayarkan','Sisa Pembayaran','Keterangan','Payment'] if c in df_budget.columns]
    if show_cols:
        st.dataframe(df_budget[show_cols], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# BUDGET ENGAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "engagement":
    page_header("💍 Budget Engagement Day")
    if df_engagement.empty:
        st.info("Data engagement belum tersedia. Pastikan GID_BUDGETING sudah diisi di Secrets.")
    else:
        total_e  = df_engagement['Budget_Num'].sum() if 'Budget_Num' in df_engagement.columns else 0
        actual_e = df_engagement['Actual_Num'].sum() if 'Actual_Num' in df_engagement.columns else 0
        c1,c2,c3 = st.columns(3)
        c1.metric("Budget",  fmt_rp(total_e))
        c2.metric("Actual",  fmt_rp(actual_e))
        c3.metric("Selisih", fmt_rp(actual_e - total_e))
        item_col  = next((c for c in ['ITEM','Item'] if c in df_engagement.columns), None)
        show_cols = [c for c in [item_col,'BRAND','BUDGET','ACTUAL','DISCOUNT','STATUS','STORE/LINK'] if c and c in df_engagement.columns]
        if show_cols:
            st.dataframe(df_engagement[show_cols], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESERAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "seserahan":
    page_header("🎁 Seserahan")
    done_s  = safe_sum(df_seserahan,'DONE')
    total_s = len(df_seserahan)
    m1,m2,m3 = st.columns(3)
    m1.metric("Total Item",f"{total_s}"); m2.metric("✅ Siap",f"{done_s}"); m3.metric("⏳ Belum",f"{total_s-done_s}")
    st.markdown(progress_bar_html((done_s/total_s*100) if total_s>0 else 0, "Progress"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_f, col_s2 = st.columns([1,3])
    with col_f:
        flt = st.radio("Filter:", ["Semua","Belum","Siap"], horizontal=True, key="ses_flt")
    with col_s2:
        q = st.text_input("Cari...", placeholder="Cari nama item seserahan...", label_visibility="collapsed", key="ses_q")

    df_s = df_seserahan.copy()
    if flt == "Belum" and 'DONE' in df_s.columns:
        df_s = df_s[df_s['DONE'] == False]
    elif flt == "Siap" and 'DONE' in df_s.columns:
        df_s = df_s[df_s['DONE'] == True]
    df_s = search_filter_df(df_s, ['LIST SESERAHAN','DETAIL'], q)
    if 'DONE' in df_s.columns:
        df_s = df_s.copy()
        df_s['Status'] = df_s['DONE'].map({True:'✅ Siap', False:'⏳ Belum'})
    show = [c for c in ['LIST SESERAHAN','DETAIL','BRAND','MODEL','NORMAL PRICE','FINAL PRICE','STORE/LINK','Status'] if c in df_s.columns]
    if show:
        st.dataframe(df_s[show], use_container_width=True, hide_index=True)
    if 'Final_Num' in df_seserahan.columns:
        total_rp = df_seserahan['Final_Num'].sum()
        if total_rp > 0:
            st.markdown(f'<div class="info-box"><b>💰 Estimasi Total:</b> {fmt_rp(total_rp)}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAHAR
# ─────────────────────────────────────────────────────────────────────────────
elif page == "mahar":
    page_header("💎 Mahar")
    if df_mahar.empty or 'LIST MAHAR' not in df_mahar.columns:
        st.info("Data mahar belum diisi di spreadsheet.")
    else:
        done_m = safe_sum(df_mahar,'DONE'); total_m = len(df_mahar)
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Item",f"{total_m}"); m2.metric("✅ Siap",f"{done_m}"); m3.metric("⏳ Belum",f"{total_m-done_m}")
        st.markdown(progress_bar_html((done_m/total_m*100) if total_m>0 else 0,"Progress Mahar"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        df_m = df_mahar.copy()
        if 'DONE' in df_m.columns:
            df_m['Status'] = df_m['DONE'].map({True:'✅ Siap', False:'⏳ Belum'})
        show = [c for c in ['LIST MAHAR','BRAND','ESTIMASI','FINAL PRICE','Status'] if c in df_m.columns]
        st.dataframe(df_m[show], use_container_width=True, hide_index=True)
        total_est   = df_mahar['Est_Num'].sum()   if 'Est_Num'   in df_mahar.columns else 0
        total_final = df_mahar['Final_Num'].sum() if 'Final_Num' in df_mahar.columns else 0
        if total_est > 0 or total_final > 0:
            st.markdown(f'<div class="info-box"><b>💰 Estimasi:</b> {fmt_rp(total_est)}<br><b>💰 Final:</b> {fmt_rp(total_final)}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HIAS SESERAHAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "hias":
    page_header("🌸 Hias Seserahan & Mahar")
    if df_hias.empty or 'LIST' not in df_hias.columns:
        st.info("Data hias seserahan belum diisi.")
    else:
        done_h = safe_sum(df_hias,'DONE'); total_h = len(df_hias)
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Item",f"{total_h}"); m2.metric("✅ Siap",f"{done_h}"); m3.metric("⏳ Belum",f"{total_h-done_h}")
        st.markdown(progress_bar_html((done_h/total_h*100) if total_h>0 else 0,"Progress Hias"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        df_h = df_hias.copy()
        if 'DONE' in df_h.columns:
            df_h['Status'] = df_h['DONE'].map({True:'✅ Siap', False:'⏳ Belum'})
        show = [c for c in ['LIST','BRAND','ESTIMASI','FINAL PRICE','Status'] if c in df_h.columns]
        st.dataframe(df_h[show], use_container_width=True, hide_index=True)
        total_est_h = df_hias['Est_Num'].sum() if 'Est_Num' in df_hias.columns else 0
        if total_est_h > 0:
            st.markdown(f'<div class="info-box"><b>💰 Estimasi Total:</b> {fmt_rp(total_est_h)}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TO-DO & DOKUMEN KUA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "todo":
    page_header("📋 To-Do & Dokumen KUA")
    tab1, tab2 = st.tabs(["📌 To-Do Tasks","📄 Dokumen KUA"])
    with tab1:
        if df_tasks.empty:
            st.info("Data tasks belum tersedia.")
        else:
            done_dp = safe_sum(df_tasks,'DP_Done'); done_fp = safe_sum(df_tasks,'FP_Done'); total_t = len(df_tasks)
            c1,c2,c3 = st.columns(3)
            c1.metric("Total Kegiatan",f"{total_t}"); c2.metric("💰 DP Selesai",f"{done_dp}"); c3.metric("✅ Lunas",f"{done_fp}")
            st.markdown(progress_bar_html((done_fp/total_t*100) if total_t>0 else 0,"Progress Pelunasan"), unsafe_allow_html=True)
            df_ts = df_tasks.copy()
            show = ['No','Kegiatan']
            if 'DP_Done' in df_ts.columns:
                df_ts['DP']    = df_ts['DP_Done'].map({True:'✅', False:'⏳'})
                show.append('DP')
            if 'FP_Done' in df_ts.columns:
                df_ts['Lunas'] = df_ts['FP_Done'].map({True:'✅', False:'⏳'})
                show.append('Lunas')
            st.dataframe(df_ts[[c for c in show if c in df_ts.columns]], use_container_width=True, hide_index=True)
    with tab2:
        if df_kua.empty:
            st.info("Data dokumen KUA belum tersedia.")
        else:
            done_k = safe_sum(df_kua,'Done'); total_k = len(df_kua)
            k1,k2,k3 = st.columns(3)
            k1.metric("Total Dokumen",f"{total_k}"); k2.metric("✅ Selesai",f"{done_k}"); k3.metric("⏳ Belum",f"{total_k-done_k}")
            st.markdown(progress_bar_html((done_k/total_k*100) if total_k>0 else 0,"Kelengkapan"), unsafe_allow_html=True)
            df_ks = df_kua.copy()
            if 'Done' in df_ks.columns:
                df_ks['Status'] = df_ks['Done'].map({True:'✅ Selesai', False:'⏳ Belum'})
            show = [c for c in ['Dokumen','Status'] if c in df_ks.columns]
            if not show:
                show = df_ks.columns[:2].tolist()
            st.dataframe(df_ks[show], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAMU UNDANGAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "tamu":
    page_header("👥 Tamu Undangan")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("👩 CPW",            f"{len(df_cpw):,}")
    c2.metric("👨 CPP",            f"{len(df_cpp):,}")
    c3.metric("👥 Total Diundang", f"{len(df_all_tamu):,}")
    c4.metric("📋 Tanpa Undangan", f"{len(df_no_inv):,}")
    st.markdown("<br>", unsafe_allow_html=True)
    tab1,tab2,tab3 = st.tabs(["📋 Semua Tamu","👩 CPW","👨 CPP"])

    def render_tamu_tab(df, label_key):
        q_col,f_col = st.columns([3,1])
        with q_col:
            q = st.text_input("Cari...", placeholder="Nama atau instansi...", label_visibility="collapsed", key=f"q_{label_key}")
        with f_col:
            inst_opts = ["Semua"]
            if 'Instansi' in df.columns:
                vals = col_as_series(df,'Instansi').str.strip().unique().tolist()
                inst_opts += sorted([x for x in vals if x])
            inst_sel = st.selectbox("Instansi", inst_opts, label_visibility="collapsed", key=f"inst_{label_key}")
        df_f = search_filter_df(df, ['Nama','Instansi'], q)
        if inst_sel != "Semua" and 'Instansi' in df_f.columns:
            df_f = df_f[col_as_series(df_f,'Instansi').str.strip() == inst_sel]
        st.markdown(f"<div style='font-size:0.82em;color:#8b6f5c;margin-bottom:6px;'>Menampilkan {len(df_f)} tamu</div>", unsafe_allow_html=True)
        show = [c for c in ['Nama','Instansi','Ket','Side'] if c in df_f.columns]
        if show:
            st.dataframe(df_f[show], use_container_width=True, hide_index=True, height=400)
        if 'Instansi' in df_f.columns and len(df_f) > 0:
            ic = col_as_series(df_f,'Instansi').value_counts().head(10).reset_index()
            ic.columns = ['Instansi','Jumlah']
            ic = ic[ic['Instansi'].str.strip() != '']
            if not ic.empty:
                fig = px.bar(ic, x='Jumlah', y='Instansi', orientation='h', title='Top Instansi',
                             color='Jumlah', color_continuous_scale='Oryel')
                fig.update_layout(**plotly_defaults(), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab1: render_tamu_tab(df_all_tamu, "all")
    with tab2: render_tamu_tab(df_cpw, "cpw")
    with tab3: render_tamu_tab(df_cpp, "cpp")

    if not df_no_inv.empty:
        with st.expander(f"📋 Tamu Tanpa Undangan ({len(df_no_inv)} orang)"):
            show_ni = [c for c in df_no_inv.columns if not str(c).startswith('_col')][:4]
            if show_ni:
                st.dataframe(df_no_inv[show_ni], use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLAYLIST
# ─────────────────────────────────────────────────────────────────────────────
elif page == "playlist":
    page_header("🎵 Playlist Wedding")
    st.markdown("""<div class="info-box">
        <b>🎤 Vendor Entertainment</b><br>
        Lengkapi detail vendor di tab <i>Playlist Wedding</i> pada spreadsheet.
    </div>""", unsafe_allow_html=True)
    st.markdown("#### 🎶 Request Lagu")
    if df_playlist.empty:
        st.info("Belum ada lagu. Tambahkan di tab Playlist Wedding pada spreadsheet.")
    else:
        q = st.text_input("Cari lagu atau penyanyi...", placeholder="Ketik judul atau nama penyanyi...",
                          label_visibility="collapsed", key="playlist_q")
        search_cols = [df_playlist.columns[1]]
        if len(df_playlist.columns) > 2:
            search_cols.append(df_playlist.columns[2])
        df_pl = search_filter_df(df_playlist, search_cols, q)
        show_pl = [c for c in df_pl.columns if not str(c).startswith('_') and not str(c).startswith('col')][:5]
        if show_pl:
            st.dataframe(df_pl[show_pl], use_container_width=True, hide_index=True)
        st.markdown(f"<div style='font-size:0.82em;color:#8b6f5c;'>Total {len(df_pl)} lagu</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.express as px
import io

# ==========================================
# CONFIG & PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="Aplikasi Keuangan Keluarga DY",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "data_keuangan.json"

# Custom Styling (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric label {
        font-weight: 600;
        color: #555555;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS & DATA MANAGEMENT (FIXED)
# ==========================================
def load_data():
    """Membaca data dari file JSON menggunakan pandas agar format konsisten."""
    if os.path.exists(DATA_FILE):
        try:
            df_loaded = pd.read_json(DATA_FILE)
            if not df_loaded.empty:
                # Pastikan kolom wajib tersedia
                cols = ["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal"]
                for c in cols:
                    if c not in df_loaded.columns:
                        df_loaded[c] = "-"
                return df_loaded
        except Exception:
            pass
    return pd.DataFrame(columns=["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal"])

def save_data(df_input):
    """Menyimpan dataframe ke file JSON tanpa error serialization."""
    clean_df = df_input.copy()
    # Hapus kolom temporary tanggal_dt jika ada agar tidak bentrok JSON serialization
    if "tanggal_dt" in clean_df.columns:
        clean_df = clean_df.drop(columns=["tanggal_dt"])
    clean_df.to_json(DATA_FILE, orient="records", indent=4)

def format_rupiah(angka):
    try:
        return f"Rp {float(angka):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

# Initialize Data State
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df.copy()

# Buat kolom temporary tanggal_dt khusus untuk pengurutan dan grafik
if not df.empty:
    df["tanggal_dt"] = pd.to_datetime(df["tanggal"], format="%d/%m/%Y", errors="coerce")
else:
    df["tanggal_dt"] = pd.Series(dtype="datetime64[ns]")

# ==========================================
# CALCULATIONS
# ==========================================
pemasukan_total = int(df[df["jenis"] == "PEMASUKAN"]["nominal"].sum())
pengeluaran_total = int(df[df["jenis"] == "PENGELUARAN"]["nominal"].sum())
setor_tabungan_total = int(df[df["jenis"] == "SETOR TABUNGAN"]["nominal"].sum())
tarik_tabungan_total = int(df[df["jenis"] == "TARIK TABUNGAN"]["nominal"].sum())

# Saldo Dompet Utama
saldo_utama = pemasukan_total - pengeluaran_total - setor_tabungan_total + tarik_tabungan_total
# Total Seluruh Tabungan
total_tabungan_bersih = setor_tabungan_total - tarik_tabungan_total

# Breakdown Tabungan Per Pos
tabungan_df = df[df["jenis"].isin(["SETOR TABUNGAN", "TARIK TABUNGAN"])].copy()
if not tabungan_df.empty:
    tabungan_summary = tabungan_df.groupby(["pos_tabungan", "jenis"])["nominal"].sum().unstack(fill_value=0)
    if "SETOR TABUNGAN" not in tabungan_summary.columns:
        tabungan_summary["SETOR TABUNGAN"] = 0
    if "TARIK TABUNGAN" not in tabungan_summary.columns:
        tabungan_summary["TARIK TABUNGAN"] = 0
    tabungan_summary["Saldo Akhir"] = tabungan_summary["SETOR TABUNGAN"] - tabungan_summary["TARIK TABUNGAN"]
else:
    tabungan_summary = pd.DataFrame(columns=["SETOR TABUNGAN", "TARIK TABUNGAN", "Saldo Akhir"])

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("💳 Navigation & Menu")
menu = st.sidebar.radio(
    "Pilih Menu:",
    ["Dashboard & Ringkasan", "Tambah Transaksi", "Manajemen Tabungan", "Riwayat & Hapus Data", "Ekspor & Backup Data"]
)

st.sidebar.markdown("---")
st.sidebar.caption("DY Finance App v2.0 - Fixed & Enhanced")

# ==========================================
# MENU 1: DASHBOARD & RINGKASAN
# ==========================================
if menu == "Dashboard & Ringkasan":
    st.title("📊 Dashboard Keuangan Keluarga DY")
    st.caption("Ringkasan arus kas dan alokasi tabungan keluarga secara real-time.")
    
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Saldo Dompet Utama", format_rupiah(saldo_utama), 
                  delta="DEFISIT!" if saldo_utama < 0 else None, delta_color="inverse")
    with col2:
        st.metric("📈 Total Pemasukan", format_rupiah(pemasukan_total))
    with col3:
        st.metric("📉 Total Pengeluaran", format_rupiah(pengeluaran_total))
    with col4:
        st.metric("🏦 Total Seluruh Tabungan", format_rupiah(total_tabungan_bersih))
    
    if saldo_utama < 0:
        st.error("⚠️ **Peringatan Defisit!** Pengeluaran dan alokasi tabungan melebihi pemasukan utama.")

    st.markdown("---")
    
    # Visualisasi
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Tren Alur Keuangan")
        if not df.empty:
            chart_df = df.dropna(subset=["tanggal_dt"]).sort_values("tanggal_dt")
            fig_line = px.line(
                chart_df, x="tanggal_dt", y="nominal", color="jenis",
                markers=True, title="Arus Masuk/Keluar Uang",
                labels={"tanggal_dt": "Tanggal", "nominal": "Nominal (Rp)"}
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Belum ada data transaksi.")
            
    with c2:
        st.subheader("🍕 Distribusi Pengeluaran")
        df_pengeluaran = df[df["jenis"] == "PENGELUARAN"]
        if not df_pengeluaran.empty:
            fig_pie = px.pie(
                df_pengeluaran, names="kategori", values="nominal",
                title="Kategori Pengeluaran", hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Belum ada data pengeluaran.")

# ==========================================
# MENU 2: TAMBAH TRANSAKSI
# ==========================================
elif menu == "Tambah Transaksi":
    st.title("📝 Input Transaksi Baru")
    
    with st.form("form_transaksi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tanggal_input = st.date_input("Tanggal Transaksi", value=date.today(), max_value=date.today())
            jenis_input = st.selectbox("Jenis Transaksi", ["PEMASUKAN", "PENGELUARAN"])
        with col2:
            kategori_input = st.text_input("Kategori", placeholder="contoh: Gaji, Makanan, Belanja, Listrik")
            nominal_input = st.number_input("Nominal (Rp)", min_value=1, step=10000)
            
        keterangan_input = st.text_area("Keterangan Catatan", placeholder="Detail deskripsi transaksi...")
        
        submitted = st.form_submit_button("💾 Simpan Transaksi")
        
        if submitted:
            new_id = int(datetime.now().timestamp() * 1000)
            tgl_str = tanggal_input.strftime("%d/%m/%Y")
            
            new_row = {
                "id": int(new_id),
                "tanggal": str(tgl_str),
                "jenis": str(jenis_input),
                "pos_tabungan": "-",
                "kategori": str(kategori_input) if kategori_input else "Umum",
                "keterangan": str(keterangan_input),
                "nominal": int(nominal_input)
            }
            
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"Berhasil menyimpan {jenis_input} sebesar {format_rupiah(nominal_input)}")
            st.rerun()

# ==========================================
# MENU 3: MANAJEMEN TABUNGAN (POS TERPISAH)
# ==========================================
elif menu == "Manajemen Tabungan":
    st.title("🏦 Manajemen Pos Tabungan")
    st.caption("Pisahkan tabungan berdasar pos kebutuhan (misal: Anak, Rumah, Pendidikan, dll).")
    
    st.subheader("📌 Rincian Saldo Per Pos Tabungan")
    if not tabungan_summary.empty:
        cols = st.columns(len(tabungan_summary) if len(tabungan_summary) <= 4 else 4)
        for idx, (pos, row) in enumerate(tabungan_summary.iterrows()):
            with cols[idx % 4]:
                st.metric(f"🏠 {pos}", format_rupiah(row["Saldo Akhir"]))
    else:
        st.info("Belum ada pos tabungan yang dibuat.")
        
    st.markdown("---")
    col_input, col_chart = st.columns([1, 1])
    
    with col_input:
        st.subheader("➕ Transaksi Tabungan")
        with st.form("form_tabungan", clear_on_submit=True):
            tgl_tabungan = st.date_input("Tanggal", value=date.today(), max_value=date.today())
            jenis_tabungan = st.selectbox("Aksi Tabungan", ["SETOR TABUNGAN", "TARIK TABUNGAN"])
            
            list_pos = ["Tabungan Anak", "Tabungan Rumah", "Tabungan Pendidikan", "Dana Darurat", "Lainnya"]
            pos_pilihan = st.selectbox("Pilih Pos Tabungan", list_pos)
            pos_custom = st.text_input("Atau buat Pos Baru:")
            pos_final = pos_custom.strip() if pos_custom.strip() != "" else pos_pilihan
            
            nominal_tab = st.number_input("Nominal (Rp)", min_value=1, step=50000)
            ket_tab = st.text_input("Keterangan", placeholder="contoh: Setoran bulanan")
            
            sub_tab = st.form_submit_button("💾 Proses Tabungan")
            
            if sub_tab:
                valid = True
                if jenis_tabungan == "SETOR TABUNGAN" and nominal_tab > saldo_utama:
                    st.error("Saldo Utama tidak cukup untuk disetor ke tabungan!")
                    valid = False
                elif jenis_tabungan == "TARIK TABUNGAN":
                    saldo_pos_saat_ini = tabungan_summary.loc[pos_final, "Saldo Akhir"] if pos_final in tabungan_summary.index else 0
                    if nominal_tab > saldo_pos_saat_ini:
                        st.error(f"Saldo pos '{pos_final}' tidak mencukupi! (Tersedia: {format_rupiah(saldo_pos_saat_ini)})")
                        valid = False
                
                if valid:
                    new_id = int(datetime.now().timestamp() * 1000)
                    new_row = {
                        "id": int(new_id),
                        "tanggal": str(tgl_tabungan.strftime("%d/%m/%Y")),
                        "jenis": str(jenis_tabungan),
                        "pos_tabungan": str(pos_final),
                        "kategori": "Tabungan",
                        "keterangan": str(ket_tab),
                        "nominal": int(nominal_tab)
                    }
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success(f"Berhasil {jenis_tabungan} pada pos '{pos_final}'")
                    st.rerun()

    with col_chart:
        st.subheader("📊 Visualisasi Saldo Pos Tabungan")
        if not tabungan_summary.empty:
            fig_bar = px.bar(
                tabungan_summary.reset_index(),
                x="pos_tabungan", y="Saldo Akhir",
                color="pos_tabungan",
                title="Total Saldo Tiap Pos Tabungan"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# MENU 4: RIWAYAT & HAPUS DATA
# ==========================================
elif menu == "Riwayat & Hapus Data":
    st.title("📜 Riwayat Transaksi & Kelola Data")
    
    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        st.subheader("🔍 Filter Transaksi")
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_jenis = st.multiselect("Jenis Transaksi", df["jenis"].unique(), default=df["jenis"].unique())
        with fc2:
            search_ket = st.text_input("Cari Kata Kunci (Kategori / Keterangan)", "")

        filtered_df = df[
            (df["jenis"].isin(filter_jenis)) &
            (df["keterangan"].str.contains(search_ket, case=False, na=False) | 
             df["kategori"].str.contains(search_ket, case=False, na=False))
        ].copy()

        display_df = filtered_df.copy()
        display_df["nominal_formatted"] = display_df["nominal"].apply(format_rupiah)
        
        st.dataframe(
            display_df[["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal_formatted"]],
            column_config={
                "id": "ID", "tanggal": "Tanggal", "jenis": "Jenis", 
                "pos_tabungan": "Pos Tabungan", "kategori": "Kategori", 
                "keterangan": "Keterangan", "nominal_formatted": "Nominal"
            },
            use_container_width=True, hide_index=True
        )

        st.markdown("---")
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            st.subheader("🗑️ Hapus Per Item")
            id_to_delete = st.number_input("Masukkan ID Transaksi:", step=1, value=0)
            if st.button("Hapus Transaksi", type="secondary"):
                if id_to_delete in df["id"].values:
                    st.session_state.df = df[df["id"] != id_to_delete]
                    save_data(st.session_state.df)
                    st.success(f"Transaksi ID {id_to_delete} berhasil dihapus.")
                    st.rerun()
                else:
                    st.error("ID Transaksi tidak ditemukan.")
                    
        with col_del2:
            st.subheader("⚠️ Reset Semua Data")
            confirm_reset = st.checkbox("Konfirmasi reset seluruh data.")
            if st.button("🚨 Hapus Semua Data", type="primary", disabled=not confirm_reset):
                st.session_state.df = pd.DataFrame(columns=["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal"])
                save_data(st.session_state.df)
                st.success("Seluruh data berhasil direset!")
                st.rerun()

# ==========================================
# MENU 5: EKSPOR & BACKUP DATA
# ==========================================
elif menu == "Ekspor & Backup Data":
    st.title("📤 Ekspor Laporan & Backup Data")
    st.info("Unduh backup data secara berkala agar data keuangan kamu aman selamanya.")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.subheader("📥 Download Excel Laporan")
        if not df.empty:
            buffer = io.BytesIO()
            clean_export = df.drop(columns=["tanggal_dt"], errors="ignore")
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                clean_export.to_excel(writer, sheet_name='Semua_Transaksi', index=False)
                if not tabungan_summary.empty:
                    tabungan_summary.to_excel(writer, sheet_name='Ringkasan_Tabungan')
            
            st.download_button(
                label="📊 Download File Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"Laporan_Keuangan_{date.today().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Belum ada data untuk diunduh.")

    with col_exp2:
        st.subheader("📂 Backup & Restore JSON")
        if not df.empty:
            clean_json = df.drop(columns=["tanggal_dt"], errors="ignore")
            json_bytes = clean_json.to_json(orient="records", indent=4).encode('utf-8')
            st.download_button(
                label="💾 Download Backup JSON",
                data=json_bytes,
                file_name="backup_data_keuangan.json",
                mime="application/json"
            )
            
        st.markdown("---")
        st.markdown("**Restore Data Backup:**")
        uploaded_file = st.file_uploader("Upload File Backup (.json)", type=["json"])
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_json(uploaded_file)
                st.session_state.df = uploaded_df
                save_data(uploaded_df)
                st.success("Data berhasil dipulihkan!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memulihkan file: {e}")

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
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #1E88E5;
        margin-bottom: 10px;
    }
    .stMetric label {
        font-weight: 600;
        color: #555555;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS & DATA MANAGEMENT
# ==========================================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return pd.DataFrame(data)
        except Exception:
            pass
    return pd.DataFrame(columns=["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal"])

def save_data(df):
    data = df.to_dict(orient="records")
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# Initialize Data
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# Format tanggal jika dataframe tidak kosong
if not df.empty:
    df["tanggal_dt"] = pd.to_datetime(df["tanggal"], format="%d/%m/%Y", errors="coerce")
else:
    df["tanggal_dt"] = pd.Series(dtype="datetime64[ns]")

# ==========================================
# CALCULATIONS
# ==========================================
pemasukan_total = df[df["jenis"] == "PEMASUKAN"]["nominal"].sum()
pengeluaran_total = df[df["jenis"] == "PENGELUARAN"]["nominal"].sum()
setor_tabungan_total = df[df["jenis"] == "SETOR TABUNGAN"]["nominal"].sum()
tarik_tabungan_total = df[df["jenis"] == "TARIK TABUNGAN"]["nominal"].sum()

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
# SIDEBAR NAVIGATION & BACKUP
# ==========================================
st.sidebar.title("💳 Navigation & Settings")
menu = st.sidebar.radio(
    "Pilih Menu:",
    ["Dashboard & Ringkasan", "Tambah Transaksi", "Manajemen Tabungan", "Riwayat & Hapus Data", "Ekspor & Backup Data"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup Data Status")
st.sidebar.caption("Gunakan menu **Ekspor & Backup Data** agar data keuanganmu aman selamanya.")

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
        st.error("⚠️ **Peringatan Defisit!** Pengeluaran dan alokasi tabungan melebihi pemasukanmu.")

    st.markdown("---")
    
    # Grafik Section
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📈 Tren Transaksi Keuangan")
        if not df.empty:
            chart_df = df.copy().sort_values("tanggal_dt")
            fig_line = px.line(
                chart_df, x="tanggal_dt", y="nominal", color="jenis",
                markers=True, title="Alur Keluar Masuk Uang seiring Waktu",
                labels={"tanggal_dt": "Tanggal", "nominal": "Nominal (Rp)"}
            )
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Belum ada data transaksi untuk menampilkan grafik.")
            
    with c2:
        st.subheader("🍕 Distribusi Pengeluaran")
        df_pengeluaran = df[df["jenis"] == "PENGELUARAN"]
        if not df_pengeluaran.empty:
            fig_pie = px.pie(
                df_pengeluaran, names="kategori", values="nominal",
                title="Pengeluaran Berdasarkan Kategori", hole=0.4
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
                "id": new_id,
                "tanggal": tgl_str,
                "jenis": jenis_input,
                "pos_tabungan": "-",
                "kategori": kategori_input if kategori_input else "Umum",
                "keterangan": keterangan_input,
                "nominal": int(nominal_input)
            }
            
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"Berhasil menyimpan {jenis_input} sebesar {format_rupiah(nominal_input)}")
            st.rerun()

# ==========================================
# MENU 3: MANAJEMEN TABUNGAN (POS SEPARATED)
# ==========================================
elif menu == "Manajemen Tabungan":
    st.title("🏦 Manajemen & Pos Tabungan")
    st.caption("Kelola dan pisahkan tabungan berdasarkan kebutuhan (Anak, Rumah, Darurat, dll).")
    
    # Overview Tabungan per Pos
    st.subheader("📌 Rincian Saldo Per Pos Tabungan")
    if not tabungan_summary.empty:
        cols = st.columns(len(tabungan_summary) if len(tabungan_summary) <= 4 else 4)
        for idx, (pos, row) in enumerate(tabungan_summary.iterrows()):
            with cols[idx % 4]:
                st.metric(f"🏠 Pos: {pos}", format_rupiah(row["Saldo Akhir"]))
    else:
        st.info("Belum ada tabungan yang dibuat.")
        
    st.markdown("---")
    
    col_input, col_chart = st.columns([1, 1])
    
    with col_input:
        st.subheader("➕ Transaksi Tabungan")
        with st.form("form_tabungan", clear_on_submit=True):
            tgl_tabungan = st.date_input("Tanggal", value=date.today(), max_value=date.today())
            jenis_tabungan = st.selectbox("Aksi Tabungan", ["SETOR TABUNGAN", "TARIK TABUNGAN"])
            
            list_pos = ["Tabungan Anak", "Tabungan Rumah", "Tabungan Pendidikan", "Dana Darurat", "Investasi", "Lainnya"]
            pos_pilihan = st.selectbox("Pilih / Tambah Pos Tabungan", list_pos)
            pos_custom = st.text_input("Atau ketik Pos Baru jika tidak ada di list di atas:")
            pos_final = pos_custom.strip() if pos_custom.strip() != "" else pos_pilihan
            
            nominal_tab = st.number_input("Nominal (Rp)", min_value=1, step=50000)
            ket_tab = st.text_input("Keterangan", placeholder="contoh: Celengan bulanan anak")
            
            sub_tab = st.form_submit_button("💾 Proses Tabungan")
            
            if sub_tab:
                # Validasi Saldo Utama jika SETOR
                if jenis_tabungan == "SETOR TABUNGAN" and nominal_tab > saldo_utama:
                    st.error("Saldo Utama tidak mencukupi untuk disetor ke tabungan!")
                # Validasi Saldo Pos Tabungan jika TARIK
                elif jenis_tabungan == "TARIK TABUNGAN":
                    saldo_pos_saat_ini = tabungan_summary.loc[pos_final, "Saldo Akhir"] if pos_final in tabungan_summary.index else 0
                    if nominal_tab > saldo_pos_saat_ini:
                        st.error(f"Saldo pada pos '{pos_final}' tidak mencukupi! (Tersedia: {format_rupiah(saldo_pos_saat_ini)})")
                    else:
                        valid = True
                else:
                    valid = True
                
                if 'valid' in locals() and valid:
                    new_id = int(datetime.now().timestamp() * 1000)
                    new_row = {
                        "id": new_id,
                        "tanggal": tgl_tabungan.strftime("%d/%m/%Y"),
                        "jenis": jenis_tabungan,
                        "pos_tabungan": pos_final,
                        "kategori": "Tabungan",
                        "keterangan": ket_tab,
                        "nominal": int(nominal_tab)
                    }
                    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(st.session_state.df)
                    st.success(f"Berhasil {jenis_tabungan} untuk pos {pos_final}")
                    st.rerun()

    with col_chart:
        st.subheader("📊 Visualisasi Saldo Tabungan")
        if not tabungan_summary.empty:
            fig_bar = px.bar(
                tabungan_summary.reset_index(),
                x="pos_tabungan", y="Saldo Akhir",
                color="pos_tabungan", text_auto='.2s',
                title="Perbandingan Saldo Tiap Pos Tabungan"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# MENU 4: RIWAYAT & HAPUS DATA
# ==========================================
elif menu == "Riwayat & Hapus Data":
    st.title("📜 Riwayat Transaksi & Filter")
    
    if df.empty:
        st.info("Belum ada riwayat transaksi.")
    else:
        # Filter Section
        st.subheader("🔍 Filter Data")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_jenis = st.multiselect("Jenis Transaksi", df["jenis"].unique(), default=df["jenis"].unique())
        with fc2:
            filter_pos = st.multiselect("Pos Tabungan", df["pos_tabungan"].unique(), default=df["pos_tabungan"].unique())
        with fc3:
            search_ket = st.text_input("Cari Keterangan / Kategori", "")

        # Apply Filters
        filtered_df = df[
            (df["jenis"].isin(filter_jenis)) &
            (df["pos_tabungan"].isin(filter_pos)) &
            (df["keterangan"].str.contains(search_ket, case=False, na=False) | 
             df["kategori"].str.contains(search_ket, case=False, na=False))
        ].copy()

        st.markdown(f"**Menampilkan {len(filtered_df)} dari {len(df)} transaksi:**")

        # Tampilkan Data Frame dengan Format Rupiah
        display_df = filtered_df.copy()
        display_df["nominal_formatted"] = display_df["nominal"].apply(format_rupiah)
        
        st.dataframe(
            display_df[["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal_formatted"]],
            column_config={
                "id": "ID",
                "tanggal": "Tanggal",
                "jenis": "Jenis",
                "pos_tabungan": "Pos Tabungan",
                "kategori": "Kategori",
                "keterangan": "Keterangan",
                "nominal_formatted": "Nominal"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        
        # Hapus per Item & All Item
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            st.subheader("🗑️ Hapus Per Item")
            id_to_delete = st.number_input("Masukkan ID Transaksi yang ingin dihapus:", step=1, val=0)
            if st.button("Hapus Transaksi Ini", type="secondary"):
                if id_to_delete in df["id"].values:
                    st.session_state.df = df[df["id"] != id_to_delete]
                    save_data(st.session_state.df)
                    st.success(f"Transaksi ID {id_to_delete} berhasil dihapus.")
                    st.rerun()
                else:
                    st.error("ID Transaksi tidak ditemukan.")
                    
        with col_del2:
            st.subheader("⚠️ Reset Semua Data")
            confirm_reset = st.checkbox("Saya yakin ingin menghapus SELURUH data keuangan.")
            if st.button("🚨 Hapus Semua Data", type="primary", disabled=not confirm_reset):
                st.session_state.df = pd.DataFrame(columns=["id", "tanggal", "jenis", "pos_tabungan", "kategori", "keterangan", "nominal"])
                save_data(st.session_state.df)
                st.success("Seluruh data berhasil direset!")
                st.rerun()

# ==========================================
# MENU 5: EKSPOR & BACKUP DATA
# ==========================================
elif menu == "Ekspor & Backup Data":
    st.title("📤 Ekspor & Permanensi Data (Backup)")
    st.info("💡 **Tips Data Aman Selamanya:** Karena Streamlit Share bersifat cloud bebas biaya, pastikan kamu mendownload backup data ini secara berkala dan mengunggahnya kembali jika aplikasi me-restart server.")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.subheader("📥 Download Excel Laporan")
        if not df.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Seluruh_Transaksi', index=False)
                if not tabungan_summary.empty:
                    tabungan_summary.to_excel(writer, sheet_name='Summary_Tabungan')
            
            st.download_button(
                label="📊 Download File Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"Laporan_Keuangan_Keluarga_{date.today().strftime('%Y%m%m')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Belum ada data untuk diunduh.")

    with col_exp2:
        st.subheader("📂 Backup & Restore Data (JSON)")
        
        # Download Backup JSON
        if not df.empty:
            json_str = df.to_json(orient="records", indent=4)
            st.download_button(
                label="💾 Download Backup JSON",
                data=json_str,
                file_name="backup_data_keuangan.json",
                mime="application/json"
            )
            
        st.markdown("---")
        # Restore Upload JSON
        st.markdown("**Restore / Restore Data dari File Backup:**")
        uploaded_file = st.file_uploader("Upload File Backup JSON", type=["json"])
        if uploaded_file is not None:
            try:
                uploaded_data = json.load(uploaded_file)
                st.session_state.df = pd.DataFrame(uploaded_data)
                save_data(st.session_state.df)
                st.success("Data berhasil dipulihkan dari file backup!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memuat file backup: {e}")

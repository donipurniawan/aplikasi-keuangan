import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Aplikasi Keuangan Keluarga DonnY",
    page_icon="💰",
    layout="wide"
)

# --- FUNGSI HELPER & DATA ---
FILE_DATA = "data_keuangan.json"

def format_rupiah(angka):
    return f"Rp{angka:,.0f}".replace(",", ".")

def load_data():
    if os.path.exists(FILE_DATA):
        try:
            with open(FILE_DATA, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    with open(FILE_DATA, "w") as f:
        json.dump(data, f, indent=4)

# --- FUNGSI RESET FORM (CALLBACK) ---
def reset_form_pemasukan():
    tgl_str = st.session_state.get("pem_tgl", date.today()).strftime("%d/%m/%Y")
    kat = st.session_state.get("pem_kategori", "")
    ket = st.session_state.get("pem_keterangan", "")
    nom = st.session_state.get("pem_nominal", 0)

    if nom > 0:
        transaksi_baru = {
            "tanggal": tgl_str,
            "jenis": "PEMASUKAN",
            "kategori": kat if kat else "Umum",
            "keterangan": ket,
            "nominal": int(nom)
        }
        riwayat_data = load_data()
        riwayat_data.append(transaksi_baru)
        save_data(riwayat_data)
        st.session_state["pem_kategori"] = ""
        st.session_state["pem_keterangan"] = ""
        st.session_state["pem_nominal"] = 0
        st.session_state["pesan_sukses"] = "Data pemasukan berhasil disimpan!"
    else:
        st.session_state["pesan_peringatan"] = "Nominal harus lebih dari 0."

def reset_form_pengeluaran():
    tgl_str = st.session_state.get("peng_tgl", date.today()).strftime("%d/%m/%Y")
    kat = st.session_state.get("peng_kategori", "")
    ket = st.session_state.get("peng_keterangan", "")
    nom = st.session_state.get("peng_nominal", 0)

    if nom > 0:
        transaksi_baru = {
            "tanggal": tgl_str,
            "jenis": "PENGELUARAN",
            "kategori": kat if kat else "Lain-lain",
            "keterangan": ket,
            "nominal": int(nom)
        }
        riwayat_data = load_data()
        riwayat_data.append(transaksi_baru)
        save_data(riwayat_data)
        st.session_state["peng_kategori"] = ""
        st.session_state["peng_keterangan"] = ""
        st.session_state["peng_nominal"] = 0
        st.session_state["pesan_sukses"] = "Data pengeluaran berhasil disimpan!"
    else:
        st.session_state["pesan_peringatan"] = "Nominal harus lebih dari 0."

# Hitung Ulang Saldo
riwayat = load_data()

saldo = 0
total_pemasukan = 0
total_pengeluaran = 0
total_tabungan = 0

for data in riwayat:
    nominal = data.get("nominal", 0)
    jenis = data.get("jenis", "")
    if jenis == "PEMASUKAN":
        saldo += nominal
        total_pemasukan += nominal
    elif jenis == "PENGELUARAN":
        saldo -= nominal
        total_pengeluaran += nominal
    elif jenis == "SETOR TABUNGAN":
        saldo -= nominal
        total_tabungan += nominal
    elif jenis == "TARIK TABUNGAN":
        saldo += nominal
        total_tabungan -= nominal

# --- HEADER UTAMA ---
st.title("💰 APLIKASI KEUANGAN KELUARGA DonnY")
st.caption("Kelola Pemasukan, Pengeluaran, dan Tabungan Keluarga dengan Mudah")

# Notifikasi Pesan
if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]

if "pesan_peringatan" in st.session_state:
    st.warning(st.session_state["pesan_peringatan"])
    del st.session_state["pesan_peringatan"]

# --- DASHBOARD CARD ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric(label="💰 Saldo Dompet Utama", value=format_rupiah(saldo))

with col2:
    with st.container(border=True):
        st.metric(label="📈 Total Pemasukan", value=format_rupiah(total_pemasukan))

with col3:
    with st.container(border=True):
        st.metric(label="📉 Total Pengeluaran", value=format_rupiah(total_pengeluaran))

with col4:
    with st.container(border=True):
        st.metric(label="🏦 Total Tabungan", value=format_rupiah(total_tabungan))

if saldo < 0:
    st.error(f"⚠️ PERINGATAN: Status DEFISIT! Saldo Defisit: {format_rupiah(saldo)}")

st.divider()

# --- MENU KEUANGAN (SIDEBAR) ---
menu = st.sidebar.radio(
    "=== MENU KEUANGAN ===",
    [
        "📊 Dashboard & Grafik", 
        "1. Pemasukan", 
        "2. Pengeluaran", 
        "3. Tabungan", 
        "4. Riwayat", 
        "5. Lihat Saldo", 
        "6. Excel / Import & Export", 
        "7. Hapus Data", 
        "8. Keluar/Info"
    ]
)

# 📊 DASHBOARD & GRAFIK
if menu == "📊 Dashboard & Grafik":
    st.subheader("📈 Analisis Visual Keuangan")
    
    if len(riwayat) == 0:
        st.info("Belum ada data transaksi untuk ditampilkan grafik. Silakan tambahkan transaksi terlebih dahulu.")
    else:
        df = pd.DataFrame(riwayat)
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("##### 🍕 Proporsi Pengeluaran per Kategori")
            df_pengeluaran = df[df["jenis"] == "PENGELUARAN"]
            if not df_pengeluaran.empty:
                fig_pie = px.pie(
                    df_pengeluaran, 
                    names="kategori", 
                    values="nominal", 
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.caption("Belum ada data pengeluaran.")

        with g2:
            st.markdown("##### 📊 Perbandingan Pemasukan vs Pengeluaran")
            df_summary = df[df["jenis"].isin(["PEMASUKAN", "PENGELUARAN"])]
            if not df_summary.empty:
                fig_bar = px.bar(
                    df_summary, 
                    x="jenis", 
                    y="nominal", 
                    color="jenis",
                    color_discrete_map={"PEMASUKAN": "#00CC96", "PENGELUARAN": "#EF553B"},
                    barmode="group"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.caption("Belum ada data transaksi untuk grafik batang.")

# 1. PEMASUKAN
elif menu == "1. Pemasukan":
    st.subheader("=== MENU PEMASUKAN ===")
    st.date_input("Masukkan Tanggal", max_value=date.today(), key="pem_tgl")
    st.text_input("Kategori", key="pem_kategori")
    st.text_input("Keterangan", key="pem_keterangan")
    st.number_input("Nominal (Rp)", min_value=0, step=1000, key="pem_nominal")
    
    st.button("Simpan Pemasukan", type="primary", on_click=reset_form_pemasukan)

# 2. PENGELUARAN
elif menu == "2. Pengeluaran":
    st.subheader("=== MENU PENGELUARAN ===")
    st.date_input("Masukkan Tanggal", max_value=date.today(), key="peng_tgl")
    st.text_input("Kategori", key="peng_kategori")
    st.text_input("Keterangan", key="peng_keterangan")
    st.number_input("Nominal (Rp)", min_value=0, step=1000, key="peng_nominal")
    
    st.button("Simpan Pengeluaran", type="primary", on_click=reset_form_pengeluaran)

# 3. TABUNGAN
elif menu == "3. Tabungan":
    st.subheader("=== MENU TABUNGAN ===")
    tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
    sub_pilihan = st.radio("Pilih Jenis Transaksi Tabungan", ["1. Setor Tabungan (Simpan Uang)", "2. Tarik Tabungan (Ambil Uang)"])
    kategori = st.text_input("Kategori")
    keterangan = st.text_input("Keterangan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    if st.button("Simpan Tabungan", type="primary"):
        if nominal <= 0:
            st.warning("Nominal harus lebih dari 0.")
        else:
            tgl_str = tgl_selected.strftime("%d/%m/%Y")
            if "1. Setor Tabungan" in sub_pilihan:
                if nominal > saldo:
                    st.error("Saldo tidak mencukupi untuk menabung.")
                else:
                    transaksi_baru = {
                        "tanggal": tgl_str, "jenis": "SETOR TABUNGAN",
                        "kategori": kategori if kategori else "Tabungan",
                        "keterangan": keterangan, "nominal": int(nominal)
                    }
                    riwayat.append(transaksi_baru)
                    save_data(riwayat)
                    st.success("Berhasil menyimpan ke tabungan!")
                    st.rerun()
            else:
                if nominal > total_tabungan:
                    st.error("Tabungan tidak mencukupi untuk ditarik.")
                else:
                    transaksi_baru = {
                        "tanggal": tgl_str, "jenis": "TARIK TABUNGAN",
                        "kategori": kategori if kategori else "Tabungan",
                        "keterangan": keterangan, "nominal": int(nominal)
                    }
                    riwayat.append(transaksi_baru)
                    save_data(riwayat)
                    st.success("Berhasil menarik dari tabungan!")
                    st.rerun()

# 4. RIWAYAT
elif menu == "4. Riwayat":
    st.subheader("=== RIWAYAT TRANSAKSI ===")
    sub_riwayat = st.selectbox(
        "Pilih Filter Riwayat",
        ["1. Semua Transaksi", "2. Riwayat Harian", "3. Riwayat Bulanan", "4. Riwayat Tahunan"]
    )
    
    if len(riwayat) == 0:
        st.info("Belum ada transaksi.")
    else:
        filtered_data = []
        if "1. Semua Transaksi" in sub_riwayat:
            filtered_data = riwayat[-20:]
        elif "2. Riwayat Harian" in sub_riwayat:
            cari_tgl = st.date_input("Pilih Tanggal Cari")
            tgl_target = cari_tgl.strftime("%d/%m/%Y")
            filtered_data = [item for item in riwayat if item.get("tanggal") == tgl_target]
        elif "3. Riwayat Bulanan" in sub_riwayat:
            bln = st.selectbox("Bulan", [f"{i:02d}" for i in range(1, 13)])
            thn = st.text_input("Tahun", str(datetime.now().year))
            filtered_data = [item for item in riwayat if item.get("tanggal", "").split("/")[1] == bln and item.get("tanggal", "").split("/")[2] == thn] if thn else []
        elif "4. Riwayat Tahunan" in sub_riwayat:
            thn = st.text_input("Tahun", str(datetime.now().year))
            filtered_data = [item for item in riwayat if item.get("tanggal", "").split("/")[2] == thn] if thn else []

        if not filtered_data and "1. Semua Transaksi" not in sub_riwayat:
            st.warning("Tidak ada transaksi ditemukan pada kriteria tersebut.")
        else:
            for idx, item in enumerate(reversed(filtered_data), 1):
                with st.expander(f"📌 {item.get('tanggal')} - {item.get('jenis')} - {format_rupiah(item.get('nominal', 0))}"):
                    st.write(f"**Tanggal:** {item.get('tanggal')}")
                    st.write(f"**Jenis:** {item.get('jenis')}")
                    st.write(f"**Kategori:** {item.get('kategori')}")
                    st.write(f"**Keterangan:** {item.get('keterangan')}")
                    st.write(f"**Nominal:** {format_rupiah(item.get('nominal', 0))}")

# 5. LIHAT SALDO
elif menu == "5. Lihat Saldo":
    st.subheader("=== INFORMASI KEUANGAN ===")
    st.write(f"**Saldo saat ini:** {format_rupiah(saldo)}")
    if saldo < 0:
        st.error(f"⚠️ PERINGATAN: Status DEFISIT! Saldo defisit: {format_rupiah(saldo)}")
    st.write(f"**Total Pemasukan:** {format_rupiah(total_pemasukan)}")
    st.write(f"**Total Pengeluaran:** {format_rupiah(total_pengeluaran)}")
    st.write(f"**Total Tabungan:** {format_rupiah(total_tabungan)}")

# 6. EXCEL / IMPORT & EXPORT
elif menu == "6. Excel / Import & Export":
    st.subheader("📁 Olah Data Excel / CSV")
    
    col_ex, col_im = st.columns(2)
    
    with col_ex:
        st.markdown("### 📥 Download Laporan (Export)")
        if len(riwayat) > 0:
            df_download = pd.DataFrame(riwayat)
            csv_data = df_download.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data Keuangan (CSV / Excel)",
                data=csv_data,
                file_name=f"Laporan_Keuangan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("Belum ada data untuk diunduh.")

    with col_im:
        st.markdown("### 📤 Upload Data Baru (Import)")
        uploaded_file = st.file_uploader("Upload file Excel (.xlsx) atau CSV (.csv)", type=["xlsx", "csv"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                    
                st.write("Preview Data:")
                st.dataframe(df_upload.head())
                
                if st.button("Simpan Data ke Aplikasi", type="primary"):
                    data_baru = df_upload.to_dict(orient="records")
                    riwayat.extend(data_baru)
                    save_data(riwayat)
                    st.success("Berhasil mengimpor data transaksi!")
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")

# 7. HAPUS DATA
elif menu == "7. Hapus Data":
    st.subheader("🗑️ Kelola Pembatalan / Penghapusan Data")
    
    tab1, tab2 = st.tabs(["❌ Hapus Per Transaksi (Per Unit)", "🔴 Reset Semua Data"])
    
    # --- TAB 1: HAPUS PER UNIT / PER TRANSAKSI ---
    with tab1:
        st.markdown("##### Hapus salah satu transaksi jika ada kesalahan input:")
        if len(riwayat) == 0:
            st.info("Belum ada data transaksi yang dapat dihapus.")
        else:
            daftar_pilihan = []
            for idx, item in enumerate(riwayat):
                label = f"[{idx+1}] {item.get('tanggal')} | {item.get('jenis')} | {item.get('kategori')} | {format_rupiah(item.get('nominal', 0))} ({item.get('keterangan', '-')})"
                daftar_pilihan.append((idx, label))
            
            pilihan = st.selectbox(
                "Pilih transaksi yang ingin dihapus:",
                options=[p[0] for p in daftar_pilihan],
                format_func=lambda x: [p[1] for p in daftar_pilihan if p[0] == x][0]
            )
            
            if st.button("Hapus Transaksi Ini", type="primary"):
                transaksi_dihapus = riwayat.pop(pilihan)
                save_data(riwayat)
                st.success(f"Transaksi '{transaksi_dihapus.get('jenis')}' sebesar {format_rupiah(transaksi_dihapus.get('nominal', 0))} berhasil dihapus!")
                st.rerun()

    # --- TAB 2: RESET SEMUA ---
    with tab2:
        st.warning("Tindakan ini akan menghapus SELURUH catatan transaksi tanpa terkecuali!")
        konfirmasi = st.checkbox("Saya yakin ingin menghapus SELURUH data transaksi.")
        if konfirmasi:
            if st.button("🔴 HAPUS SEMUA DATA SEKARANG", type="primary"):
                save_data([])
                st.success("Semua data transaksi berhasil dihapus!")
                st.rerun()

# 8. KELUAR / INFO
elif menu == "8. Keluar/Info":
    st.info("""
    ===============================  
    === TERIMA KASIH TELAH MENGGUNAKAN ===  
         APLIKASI KEUANGAN KELUARGA DY  
    by.doni.p  
    ===============================
    """)

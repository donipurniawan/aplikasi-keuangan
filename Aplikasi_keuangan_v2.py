import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Aplikasi Keuangan Keluarga DY",
    page_icon="💰",
    layout="wide"  # Menggunakan layar lebar agar grafik lebih leluasa
)

# --- INISIALISASI SESSION STATE (Memori Input agar tidak hilang saat pindah menu) ---
if "pem_kategori" not in st.session_state:
    st.session_state["pem_kategori"] = ""
if "pem_keterangan" not in st.session_state:
    st.session_state["pem_keterangan"] = ""
if "pem_nominal" not in st.session_state:
    st.session_state["pem_nominal"] = 0

if "peng_kategori" not in st.session_state:
    st.session_state["peng_kategori"] = ""
if "peng_keterangan" not in st.session_state:
    st.session_state["peng_keterangan"] = ""
if "peng_nominal" not in st.session_state:
    st.session_state["peng_nominal"] = 0

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
st.title("💰 APLIKASI KEUANGAN KELUARGA DY")
st.caption("Kelola Pemasukan, Pengeluaran, dan Tabungan Keluarga dengan Mudah")

# --- DASHBOARD CARD (Ringkasan Berwarna) ---
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
    ["📊 Dashboard & Grafik", "1. Pemasukan", "2. Pengeluaran", "3. Tabungan", "4. Riwayat", "5. Lihat Saldo", "6. Hapus Data", "7. Keluar/Info"]
)

# 📊 DASHBOARD & GRAFIK (Tampilan Visual Wah)
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
    tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
    
    kategori = st.text_input("Kategori", key="pem_kategori")
    keterangan = st.text_input("Keterangan", key="pem_keterangan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000, key="pem_nominal")
    
    if st.button("Simpan Pemasukan", type="primary"):
        if nominal <= 0:
            st.warning("Nominal harus lebih dari 0.")
        else:
            tgl_str = tgl_selected.strftime("%d/%m/%Y")
            transaksi_baru = {
                "tanggal": tgl_str,
                "jenis": "PEMASUKAN",
                "kategori": kategori if kategori else "Umum",
                "keterangan": keterangan,
                "nominal": int(nominal)
            }
            riwayat.append(transaksi_baru)
            save_data(riwayat)
            st.success("Data pemasukan berhasil disimpan!")
            
            st.session_state["pem_kategori"] = ""
            st.session_state["pem_keterangan"] = ""
            st.session_state["pem_nominal"] = 0
            st.rerun()

# 2. PENGELUARAN
elif menu == "2. Pengeluaran":
    st.subheader("=== MENU PENGELUARAN ===")
    tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
    
    kategori = st.text_input("Kategori", key="peng_kategori")
    keterangan = st.text_input("Keterangan", key="peng_keterangan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000, key="peng_nominal")
    
    if st.button("Simpan Pengeluaran", type="primary"):
        if nominal <= 0:
            st.warning("Nominal harus lebih dari 0.")
        else:
            tgl_str = tgl_selected.strftime("%d/%m/%Y")
            transaksi_baru = {
                "tanggal": tgl_str,
                "jenis": "PENGELUARAN",
                "kategori": kategori if kategori else "Lain-lain",
                "keterangan": keterangan,
                "nominal": int(nominal)
            }
            riwayat.append(transaksi_baru)
            save_data(riwayat)
            st.success("Data Pengeluaran berhasil disimpan.")
            
            st.session_state["peng_kategori"] = ""
            st.session_state["peng_keterangan"] = ""
            st.session_state["peng_nominal"] = 0
            st.rerun()

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
            hari, bulan, tahun = tgl_selected.day, tgl_selected.month, tgl_selected.year
            
            if "1. Setor Tabungan" in sub_pilihan:
                if nominal > saldo:
                    st.error("Saldo tidak mencukupi untuk menabung.")
                else:
                    transaksi_baru = {
                        "tanggal": tgl_str, "hari": hari, "bulan": bulan, "tahun": tahun,
                        "jenis": "SETOR TABUNGAN", "kategori": kategori if kategori else "Tabungan", "keterangan": keterangan, "nominal": int(nominal)
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
                        "tanggal": tgl_str, "hari": hari, "bulan": bulan, "tahun": tahun,
                        "jenis": "TARIK TABUNGAN", "kategori": kategori if kategori else "Tabungan", "keterangan": keterangan, "nominal": int(nominal)
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

# 6. HAPUS DATA
elif menu == "6. Hapus Data":
    st.subheader("🗑️ Hapus / Reset Semua Data Transaksi")
    st.warning("Tindakan ini akan menghapus SELURUH catatan transaksi dan mengembalikan saldo ke Rp0.")
    
    konfirmasi = st.checkbox("Saya yakin ingin menghapus seluruh data transaksi.")
    if konfirmasi:
        if st.button("🔴 HAPUS SEMUA DATA SEKARANG", type="primary"):
            save_data([])
            st.success("Semua data transaksi berhasil dihapus!")
            st.rerun()

# 7. KELUAR / INFO
elif menu == "7. Keluar/Info":
    st.info("""
    ===============================  
    === TERIMA KASIH TELAH MENGGUNAKAN ===  
         APLIKASI KEUANGAN KELUARGA DY  
    by.doni.p  
    ===============================
    """)

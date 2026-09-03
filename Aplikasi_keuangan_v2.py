import json
import os
import streamlit as st
from datetime import datetime, date

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Aplikasi Keuangan Keluarga DY",
    page_icon="💰",
    layout="centered"
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

# Hitung Ulang Saldo dari Data JSON
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

# --- HEADER & DASHBOARD ---
st.title("===========================")
st.title("APLIKASI KEUANGAN KELUARGA")
st.title("===========================")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="💰 Saldo Dompet Utama", value=format_rupiah(saldo))
    st.metric(label="📉 Total Pengeluaran", value=format_rupiah(total_pengeluaran))
with col2:
    st.metric(label="📈 Total Pemasukan", value=format_rupiah(total_pemasukan))
    st.metric(label="🏦 Total Tabungan", value=format_rupiah(total_tabungan))

if saldo < 0:
    st.error(f"⚠️ PERINGATAN: Status DEFISIT! Saldo Defisit: {format_rupiah(saldo)}")

st.divider()

# --- MENU KEUANGAN ---
menu = st.sidebar.radio(
    "=== MENU KEUANGAN ===",
    ["1. Pemasukan", "2. Pengeluaran", "3. Tabungan", "4. Riwayat", "5. Lihat Saldo", "6. Keluar/Info"]
)

# 1. PEMASUKAN
if menu == "1. Pemasukan":
    st.subheader("=== MENU PEMASUKAN ===")
    tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
    kategori = st.text_input("Kategori")
    keterangan = st.text_input("Keterangan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    if st.button("Simpan Pemasukan", type="primary"):
        if nominal <= 0:
            st.warning("Nominal harus lebih dari 0.")
        else:
            tgl_str = tgl_selected.strftime("%d/%m/%Y")
            transaksi_baru = {
                "tanggal": tgl_str,
                "jenis": "PEMASUKAN",
                "kategori": kategori,
                "keterangan": keterangan,
                "nominal": int(nominal)
            }
            riwayat.append(transaksi_baru)
            save_data(riwayat)
            st.success("Data pemasukan berhasil disimpan!")
            st.rerun()

# 2. PENGELUARAN
elif menu == "2. Pengeluaran":
    st.subheader("=== MENU PENGELUARAN ===")
    tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
    kategori = st.text_input("Kategori")
    keterangan = st.text_input("Keterangan")
    nominal = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    
    if st.button("Simpan Pengeluaran", type="primary"):
        if nominal <= 0:
            st.warning("Nominal harus lebih dari 0.")
        else:
            tgl_str = tgl_selected.strftime("%d/%m/%Y")
            transaksi_baru = {
                "tanggal": tgl_str,
                "jenis": "PENGELUARAN",
                "kategori": kategori,
                "keterangan": keterangan,
                "nominal": int(nominal)
            }
            riwayat.append(transaksi_baru)
            save_data(riwayat)
            st.success("Data Pengeluaran berhasil disimpan.")
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
                        "jenis": "SETOR TABUNGAN", "kategori": kategori, "keterangan": keterangan, "nominal": int(nominal)
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
                        "jenis": "TARIK TABUNGAN", "kategori": kategori, "keterangan": keterangan, "nominal": int(nominal)
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

# 6. KELUAR / INFO
elif menu == "6. Keluar/Info":
    st.info("""
    ===============================  
    === TERIMA KASIH TELAH MENGGUNAKAN ===  
         APLIKASI KEUANGAN KELUARGA DY  
    by.doni.p  
    ===============================
    """)

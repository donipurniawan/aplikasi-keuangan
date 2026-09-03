import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Inisialisasi Koneksi GSheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Masukkan URL Google Spreadsheet Anda di sini (atau ambil dari st.secrets)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/INFORMASIKAN_ID_SPREADSHEET_ANDA/edit"
WORKSHEET_NAME = "Sheet1"  # Sesuaikan dengan nama sheet Anda


def load_data():
    """Membaca data dari Google Sheets."""
    # Gunakan ttl=0 agar data yang dibaca selalu yang terbaru (tanpa cache)
    return conn.read(
        spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, ttl=0
    )


def save_data(df_new):
    """Menyimpan/Mengupdate data ke Google Sheets."""
    # Pastikan menentukan spreadsheet dan worksheet dengan jelas
    conn.update(
        spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, data=df_new
    )


def reset_form_pemasukan():
    # Contoh penggunaan save_data
    riwayat_data = load_data()

    # ... (proses penambahan/perubahan data pada riwayat_data) ...

    save_data(riwayat_data)


# --- Tampilan Streamlit ---
st.title("📊 Aplikasi Keuangan v2 (Google Sheets Integration)")

# Ambil data
df = load_data()

# Tampilkan Spreadsheet Interaktif
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("💾 Simpan ke Google Sheets"):
    try:
        save_data(edited_df)
        st.success("Berhasil memperbarui Google Sheets!")
        st.rerun()
    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

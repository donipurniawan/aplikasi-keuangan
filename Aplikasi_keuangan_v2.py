from datetime import date, datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import streamlit as st

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Aplikasi Keuangan Keluarga Donny", page_icon="💰", layout="wide"
)

# MASUKKAN URL SPREADSHEET ANDA DI SINI
SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/INFORMASIKAN_ID_SPREADSHEET_ANDA/edit"
)
WORKSHEET_NAME = "Sheet1"


# --- KONEKSI GOOGLE SHEETS VIA GSPREAD ---
def get_gspread_client():
  """Mengambil koneksi Google Sheets menggunakan kredensial dari st.secrets."""
  scopes = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]

  if "gcp_service_account" in st.secrets:
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
  elif "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    credentials = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"], scopes=scopes
    )
  else:
    st.error(
        "❌ Secrets 'gcp_service_account' belum diatur di Secrets Streamlit"
        " Cloud!"
    )
    st.stop()

  return gspread.authorize(credentials)


def load_data():
  """Membaca data dari Google Sheets."""
  try:
    gc = get_gspread_client()
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.worksheet(WORKSHEET_NAME)
    records = worksheet.get_all_records()

    if not records:
      return []

    df = pd.DataFrame(records)
    if "nominal" in df.columns:
      df["nominal"] = (
          pd.to_numeric(df["nominal"], errors="coerce").fillna(0).astype(int)
      )
    return df.to_dict(orient="records")
  except Exception as e:
    st.error(f"⚠️ Gagal membaca data dari Google Sheets: {e}")
    return []


def save_data(data_list):
  """Menyimpan seluruh data list ke Google Sheets."""
  try:
    gc = get_gspread_client()
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.worksheet(WORKSHEET_NAME)

    if not data_list:
      # Jika data kosong (saat reset/hapus semua)
      worksheet.clear()
      worksheet.append_row(
          ["tanggal", "jenis", "kategori", "keterangan", "nominal"]
      )
      return True

    df_new = pd.DataFrame(data_list)

    # Pastikan urutan kolom sesuai
    kolom = ["tanggal", "jenis", "kategori", "keterangan", "nominal"]
    for k in kolom:
      if k not in df_new.columns:
        df_new[k] = ""
    df_new = df_new[kolom]

    # Bersihkan data agar aman dikirim
    df_clean = df_new.fillna("")
    df_clean["tanggal"] = df_clean["tanggal"].astype(str)

    worksheet.clear()
    worksheet.update(
        [df_clean.columns.values.tolist()] + df_clean.values.tolist()
    )
    return True
  except Exception as e:
    st.error(f"❌ Gagal menyimpan data: {e}")
    return False


def format_rupiah(angka):
  return f"Rp{angka:,.0f}".replace(",", ".")


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
        "nominal": int(nom),
    }
    riwayat_data = load_data()
    riwayat_data.append(transaksi_baru)
    if save_data(riwayat_data):
      st.session_state["pem_kategori"] = ""
      st.session_state["pem_keterangan"] = ""
      st.session_state["pem_nom_raw"] = ""
      st.session_state["pem_nominal"] = 0
      st.session_state["pesan_sukses"] = (
          "Data pemasukan berhasil disimpan ke Google Sheets!"
      )
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
        "nominal": int(nom),
    }
    riwayat_data = load_data()
    riwayat_data.append(transaksi_baru)
    if save_data(riwayat_data):
      st.session_state["peng_kategori"] = ""
      st.session_state["peng_keterangan"] = ""
      st.session_state["peng_nom_raw"] = ""
      st.session_state["peng_nominal"] = 0
      st.session_state["pesan_sukses"] = (
          "Data pengeluaran berhasil disimpan ke Google Sheets!"
      )
  else:
    st.session_state["pesan_peringatan"] = "Nominal harus lebih dari 0."


# --- HITUNG ULANG SALDO ---
riwayat = load_data()

saldo = 0
total_pemasukan = 0
total_pengeluaran = 0
total_tabungan = 0

for data in riwayat:
  nominal = int(data.get("nominal", 0))
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
st.title("💰 APLIKASI KEUANGAN KELUARGA DONNY")
st.caption("Tersimpan Permanen & Real-time di Google Sheets")

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
    st.metric(
        label="📉 Total Pengeluaran", value=format_rupiah(total_pengeluaran)
    )

with col4:
  with st.container(border=True):
    st.metric(label="🏦 Total Tabungan", value=format_rupiah(total_tabungan))

if saldo < 0:
  st.error(
      f"⚠️ PERINGATAN: Status DEFISIT! Saldo Defisit: {format_rupiah(saldo)}"
  )

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
        "8. Keluar/Info",
    ],
)

# 📊 DASHBOARD & GRAFIK
if menu == "📊 Dashboard & Grafik":
  st.subheader("📈 Analisis Visual Keuangan")

  if len(riwayat) == 0:
    st.info(
        "Belum ada data transaksi untuk ditampilkan grafik. Silakan tambahkan"
        " transaksi terlebih dahulu."
    )
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
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_traces(
            textposition="inside", textinfo="percent+label"
        )
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
            color_discrete_map={
                "PEMASUKAN": "#00CC96",
                "PENGELUARAN": "#EF553B",
            },
            barmode="group",
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

  nom_input = st.text_input(
      "Nominal (Rp)", placeholder="Contoh: 12000", key="pem_nom_raw"
  )
  nom_clean = "".join(filter(str.isdigit, nom_input))
  nom_val = int(nom_clean) if nom_clean else 0
  st.session_state["pem_nominal"] = nom_val

  if nom_val > 0:
    st.info(f"💵 Tampilan Nominal: **{format_rupiah(nom_val)}**")

  st.button("Simpan Pemasukan", type="primary", on_click=reset_form_pemasukan)

# 2. PENGELUARAN
elif menu == "2. Pengeluaran":
  st.subheader("=== MENU PENGELUARAN ===")
  st.date_input("Masukkan Tanggal", max_value=date.today(), key="peng_tgl")
  st.text_input("Kategori", key="peng_kategori")
  st.text_input("Keterangan", key="peng_keterangan")

  nom_input = st.text_input(
      "Nominal (Rp)", placeholder="Contoh: 12000", key="peng_nom_raw"
  )
  nom_clean = "".join(filter(str.isdigit, nom_input))
  nom_val = int(nom_clean) if nom_clean else 0
  st.session_state["peng_nominal"] = nom_val

  if nom_val > 0:
    st.info(f"💵 Tampilan Nominal: **{format_rupiah(nom_val)}**")

  st.button(
      "Simpan Pengeluaran", type="primary", on_click=reset_form_pengeluaran
  )

# 3. TABUNGAN
elif menu == "3. Tabungan":
  st.subheader("=== MENU TABUNGAN ===")
  tgl_selected = st.date_input("Masukkan Tanggal", max_value=date.today())
  sub_pilihan = st.radio(
      "Pilih Jenis Transaksi Tabungan",
      ["1. Setor Tabungan (Simpan Uang)", "2. Tarik Tabungan (Ambil Uang)"],
  )
  kategori = st.text_input("Kategori")
  keterangan = st.text_input("Keterangan")

  nom_input = st.text_input("Nominal (Rp)", placeholder="Contoh: 12000")
  nom_clean = "".join(filter(str.isdigit, nom_input))
  nominal = int(nom_clean) if nom_clean else 0

  if nominal > 0:
    st.info(f"💵 Tampilan Nominal: **{format_rupiah(nominal)}**")

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
              "tanggal": tgl_str,
              "jenis": "SETOR TABUNGAN",
              "kategori": kategori if kategori else "Tabungan",
              "keterangan": keterangan,
              "nominal": int(nominal),
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
              "tanggal": tgl_str,
              "jenis": "TARIK TABUNGAN",
              "kategori": kategori if kategori else "Tabungan",
              "keterangan": keterangan,
              "nominal": int(nominal),
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
      [
          "1. Semua Transaksi",
          "2. Riwayat Harian",
          "3. Riwayat Bulanan",
          "4. Riwayat Tahunan",
      ],
  )

  if len(riwayat) == 0:
    st.info("Belum ada transaksi di Google Sheets.")
  else:
    filtered_data = []
    if "1. Semua Transaksi" in sub_riwayat:
      filtered_data = riwayat[-20:]
    elif "2. Riwayat Harian" in sub_riwayat:
      cari_tgl = st.date_input("Pilih Tanggal Cari")
      tgl_target = cari_tgl.strftime("%d/%m/%Y")
      filtered_data = [
          item for item in riwayat if str(item.get("tanggal")) == tgl_target
      ]
    elif "3. Riwayat Bulanan" in sub_riwayat:
      bln = st.selectbox("Bulan", [f"{i:02d}" for i in range(1, 13)])
      thn = st.text_input("Tahun", str(datetime.now().year))
      filtered_data = (
          [
              item
              for item in riwayat
              if str(item.get("tanggal", "")).split("/")[1] == bln
              and str(item.get("tanggal", "")).split("/")[2] == thn
          ]
          if thn
          else []
      )
    elif "4. Riwayat Tahunan" in sub_riwayat:
      thn = st.text_input("Tahun", str(datetime.now().year))
      filtered_data = (
          [
              item
              for item in riwayat
              if str(item.get("tanggal", "")).split("/")[2] == thn
          ]
          if thn
          else []
      )

    if not filtered_data and "1. Semua Transaksi" not in sub_riwayat:
      st.warning("Tidak ada transaksi ditemukan pada kriteria tersebut.")
    else:
      for idx, item in enumerate(reversed(filtered_data), 1):
        with st.expander(
            f"📌 {item.get('tanggal')} - {item.get('jenis')} -"
            f" {format_rupiah(int(item.get('nominal', 0)))}"
        ):
          st.write(f"**Tanggal:** {item.get('tanggal')}")
          st.write(f"**Jenis:** {item.get('jenis')}")
          st.write(f"**Kategori:** {item.get('kategori')}")
          st.write(f"**Keterangan:** {item.get('keterangan')}")
          st.write(
              "**Nominal:**"
              f" {format_rupiah(int(item.get('nominal', 0)))}"
          )

# 5. LIHAT SALDO
elif menu == "5. Lihat Saldo":
  st.subheader("=== INFORMASI KEUANGAN ===")
  st.write(f"**Saldo saat ini:** {format_rupiah(saldo)}")
  if saldo < 0:
    st.error(
        f"⚠️ PERINGATAN: Status DEFISIT! Saldo defisit: {format_rupiah(saldo)}"
    )
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
      csv_data = df_download.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="Download Data Keuangan (CSV / Excel)",
          data=csv_data,
          file_name=(
              f"Laporan_Keuangan_{datetime.now().strftime('%Y%m%d')}.csv"
          ),
          mime="text/csv",
          type="primary",
      )
    else:
      st.info("Belum ada data untuk diunduh.")

  with col_im:
    st.markdown("### 📤 Upload Data Baru (Import)")
    uploaded_file = st.file_uploader(
        "Upload file Excel (.xlsx) atau CSV (.csv)", type=["xlsx", "csv"]
    )

    if uploaded_file is not None:
      try:
        if uploaded_file.name.endswith(".csv"):
          df_upload = pd.read_csv(uploaded_file)
        else:
          df_upload = pd.read_excel(uploaded_file)

        st.write("Preview Data:")
        st.dataframe(df_upload.head())

        if st.button("Simpan Data ke Google Sheets", type="primary"):
          data_baru = df_upload.to_dict(orient="records")
          riwayat.extend(data_baru)
          save_data(riwayat)
          st.success("Berhasil mengimpor data transaksi ke Google Sheets!")
          st.rerun()
      except Exception as e:
        st.error(f"Gagal membaca file: {e}")

# 7. HAPUS DATA
elif menu == "7. Hapus Data":
  st.subheader("🗑️ Kelola Pembatalan / Penghapusan Data")

  tab1, tab2 = st.tabs(
      ["❌ Hapus Per Transaksi (Per Unit)", "🔴 Reset Semua Data"]
  )

  # --- TAB 1: HAPUS PER UNIT / PER TRANSAKSI ---
  with tab1:
    st.markdown("##### Hapus salah satu transaksi jika ada kesalahan input:")
    if len(riwayat) == 0:
      st.info("Belum ada data transaksi yang dapat dihapus.")
    else:
      daftar_pilihan = []
      for idx, item in enumerate(riwayat):
        label = (
            f"[{idx+1}] {item.get('tanggal')} | {item.get('jenis')} |"
            f" {item.get('kategori')} |"
            f" {format_rupiah(int(item.get('nominal', 0)))}"
            f" ({item.get('keterangan', '-')})"
        )
        daftar_pilihan.append((idx, label))

      pilihan = st.selectbox(
          "Pilih transaksi yang ingin dihapus:",
          options=[p[0] for p in daftar_pilihan],
          format_func=lambda x: [
              p[1] for p in daftar_pilihan if p[0] == x
          ][0],
      )

      if st.button("Hapus Transaksi Ini", type="primary"):
        transaksi_dihapus = riwayat.pop(pilihan)
        save_data(riwayat)
        st.success(
            f"Transaksi '{transaksi_dihapus.get('jenis')}' sebesar"
            f" {format_rupiah(int(transaksi_dihapus.get('nominal', 0)))}"
            " berhasil dihapus dari Google Sheets!"
        )
        st.rerun()

  # --- TAB 2: RESET SEMUA ---
  with tab2:
    st.warning(
        "Tindakan ini akan menghapus SELURUH catatan transaksi tanpa"
        " terkecuali!"
    )
    konfirmasi = st.checkbox(
        "Saya yakin ingin menghapus SELURUH data transaksi."
    )
    if konfirmasi:
      if st.button("🔴 HAPUS SEMUA DATA SEKARANG", type="primary"):
        save_data([])
        st.success(
            "Semua data transaksi di Google Sheets berhasil dibersihkan!"
        )
        st.rerun()

# 8. KELUAR / INFO
elif menu == "8. Keluar/Info":
  st.info("""
    ===============================  
    === TERIMA KASIH TELAH MENGGUNAKAN ===  
         APLIKASI KEUANGAN KELUARGA DONNY  
    by.doni.p  
    ===============================
    """)

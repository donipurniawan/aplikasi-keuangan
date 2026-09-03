import json
import os
from datetime import date as dt_date
def format_rupiah(angka):
    return "Rp{:,}".format(angka).replace(",", ".")
saldo = 0
total_pemasukan = 0
total_pengeluaran = 0
total_tabungan = 0
riwayat = []
if os.path.exists("data_keuangan.json"):
    with open("data_keuangan.json", "r") as file:
        try:
            riwayat = json.load(file)
            for data in riwayat :
              if data ["jenis"] == "PEMASUKAN":
                 saldo += data["nominal"]
                 total_pemasukan += data["nominal"]
              elif data ["jenis"] == "PENGELUARAN":
                 saldo -= data["nominal"]
                 total_pengeluaran += data["nominal"]
              elif data ["jenis"] == "SETOR TABUNGAN":
                 saldo -= data["nominal"]
                 total_tabungan += data["nominal"]
              elif data ["jenis"] == "TARIK TABUNGAN":
                 saldo += data["nominal"]
                 total_tabungan -= data["nominal"]
        except:
            pass
while True:
    print()
    print("===========================")
    print(  "APLIKASI KEUANGAN KELUARGA")
    print("===========================")
    print(f"💰Saldo             :{format_rupiah(saldo)}")
    print(f"📈Total Pemasukan   :{format_rupiah(total_pemasukan)}")
    print(f"📉Total pengeluaran :{format_rupiah(total_pengeluaran)}")
    print(f"🏦Total tabungan    :{format_rupiah(total_tabungan)}")
    print("=== MENU KEUANGAN ===")
    print()
    print("1. Pemasukan")
    print("2. Pengeluaran")
    print("3. Tabungan")
    print("4. Riwayat")
    print("5. Lihat Saldo")
    print("6. Keluar")
    print()
    pilihan = input("Pilih Menu (1-6): ")
    if pilihan== "1":
       print("=== MENU PEMASUKAN ===")
       while True:
           tanggal = input("Masukkan tanggal(ddmmyyyy): ")
           if len(tanggal) == 8 and tanggal.isdigit():
              hari = int(tanggal[:2])
              bulan = int(tanggal[2:4])
              tahun = int(tanggal[4:])
              try:
                 tanggal_user = dt_date(tahun, bulan, hari)
                 hari_ini = dt_date.today()
                 if tanggal_user > hari_ini:
                    print("Fomat salah! tidak boleh melewati hari ini")
                    print("Silahkan ulangi input tanggal.\n")
                 else: 
                    tanggal = f"{hari:02d}/{bulan:02d}/{tahun}"
                    break
              except ValueError :
                print("Format salah! Tanggal atau bulan tidak valid.")
                print("Silahkan ulangi input tanggal")
           else:
                print("Format harus 8 digit (ddmmyyy).")
                print("Silahkan ulangi input tanggal")
       kategori = input(f"{'Kategori':26}:")
       keterangan = input(f"{'Keterangan':26}:")
       while True:
         try:
            nominal =int(input(f"{'Nominal':26}:"))
            if nominal > 0:
               break
            else:
               print("Nominal harus lebih dari 0.")
         except ValueError:
               print("Input harus berupa angka!")
       saldo = saldo + nominal
       total_pemasukan = total_pemasukan + nominal
       riwayat.append ({"tanggal": tanggal, "jenis": "PEMASUKAN", "kategori": kategori, "keterangan": keterangan, "nominal": nominal})
       with open("data_keuangan.json", "w") as file:
              json.dump(riwayat, file, indent=4)
       print()
       print("Data pemasukan berhasil disimpan")
       print("saldo :", format_rupiah(saldo))
       input("\nTekan Enter untuk kembali ke menu...")
    elif pilihan == "2":
         print("=== MENU PENGELUARAN ===")
         while True:
           tanggal = input("Masukkan tanggal(ddmmyyyy): ")
           if len(tanggal) == 8 and tanggal.isdigit():
              hari = int(tanggal[:2])
              bulan = int(tanggal[2:4])
              tahun = int(tanggal[4:])
              try:
                 tanggal_user = dt_date(tahun, bulan, hari)
                 hari_ini = dt_date.today()
                 if tanggal_user > hari_ini:
                    print("Fomat salah! tidak boleh melewati hari ini")
                    print("Silahkan ulangi input tanggal.\n")
                 else: 
                    tanggal = f"{hari:02d}/{bulan:02d}/{tahun}"
                    break
              except ValueError :
                print("Format salah! Tanggal atau bulan tidak valid.")
                print("Silahkan ulangi input tanggal")
           else:
                print("Format harus 8 digit (ddmmyyy).")
                print("Silahkan ulangi input tanggal")
         kategori =input(f"{'Kategori':26}:")
         keterangan =input (f"{'Katerangan':26}:")
         while True:
           try:
              nominal =int(input (f"{'Nominal':26}:"))
              if nominal <= 0:
                 print("Nominal harus lebih dari 0.")
                 continue
              break
           except ValueError:
                print("input harus berupa angka!")
         saldo = saldo - nominal
         total_pengeluaran = total_pengeluaran + nominal
         if saldo < 0:
                 print("\n⚠️PERINGATAN")
                 print("Status : DEFISIT")
                 print("Saldo :", format_rupiah(saldo))
                 
         riwayat.append ({"tanggal": tanggal, "jenis": "PENGELUARAN", "kategori": kategori, "keterangan": keterangan, "nominal": nominal})
         with open("data_keuangan.json", "w") as file:
              json.dump(riwayat, file, indent=4)
         print()
         print("Data Pengeluaran berhasil disimpan.")
         print("saldo :", format_rupiah(saldo))
         input("\nTekan Enter untuk kembali ke menu...")
    elif pilihan == "3":
         print("===MENU TABUNGAN===")
         while True:
           tanggal = input("Masukkan tanggal(ddmmyyyy): ")
           if len(tanggal) == 8 and tanggal.isdigit():
              hari = int(tanggal[:2])
              bulan = int(tanggal[2:4])
              tahun = int(tanggal[4:])
              try:
                 tanggal_user = dt_date(tahun, bulan, hari)
                 hari_ini = dt_date.today()
                 if tanggal_user > hari_ini:
                    print("Fomat salah! tidak boleh melewati hari ini")
                    print("Silahkan ulangi input tanggal.\n")
                 else: 
                    tanggal = f"{hari:02d}/{bulan:02d}/{tahun}"
                    break
              except ValueError :
                print("Format salah! Tanggal atau bulan tidak valid.")
                print("Silahkan ulangi input tanggal")
           else:
                print("Format harus 8 digit (ddmmyyy).")
                print("Silahkan ulangi input tanggal")
         while True:
             print("1. Setor Tabungan(Simpan Uang)")
             print("2. Tarik Tabungan (Ambil Uang)")
             sub_pilihan = input ("Pilih jenis transaksi tabungan (1-2): ")
         
             if sub_pilihan == "1" or sub_pilihan == "2":
                break
             else:
                 print("Pilihan tidak tersedia! Silahkan masukan angka 1 atau 2.\n")
         kategori = input(f"{'Kategori':26}:")
         keterangan = input (f"{'Katerangan':26}:")
         while True:
             try:
               nominal =int(input(f"{'Nominal':26}:"))
               if nominal <=0:
                   print("Nominal harus lebih dari 0.")
                   continue
               if nominal >saldo:
                   print("Saldo tidak mencukupi.")
                   continue
               break
             except ValueError:
                print("Input harus berupa angka!")
         if sub_pilihan == "1":
             if nominal > saldo:
                 print("Saldo tidak mencukupi.")
                 input("\nTekan Enter untuk kembali...")
                 continue
             saldo -= nominal
             total_tabungan += nominal
             jenis_transaksi = "SETOR TABUNGAN"
             print("Berhasil menyimpan ke tabungan")
         else:
            if nominal > total_tabungan:
                print("Tabungan tidak mencukupi")
                input("\nTekan Enter untuk kembali...")
                continue
            saldo += nominal
            total_tabungan -= nominal
            jenis_transaksi = "TARIK TABUNGAN"
            print("Berhasil menarik dari tabungan")
         riwayat.append ({"tanggal": tanggal, "hari": hari, "bulan": bulan, "tahun": tahun, "jenis": jenis_transaksi, "kategori": kategori, "keterangan": keterangan, "nominal": nominal})
         with open("data_keuangan.json", "w") as file:
              json.dump(riwayat, file, indent=4)
         print("saldo dompet utama saat ini :", format_rupiah(saldo))
         print()
         print ("Tabungan berhasil disimpan.")
         print("saldo :", format_rupiah(saldo))
         input("\nTekan Enter untuk kembali ke menu...")
    elif pilihan == "4":
        print("===RIWAYAT TRANSAKSI===")
        print("1. Semua Transaksi")
        print("2. Riwayat Harian")
        print("3. Riwayat Bulanan")
        print("4. Riwayat Tahunan")
        print("5. Kembali")
        pilihan_riwayat = input ("Pilih Menu (1-5): ")
        if pilihan_riwayat == "1":
           if len(riwayat) == 0:
              print("Belum ada transaksi.")
           else:
             tanggal_sebelumnya = ""
             for i, data in enumerate(riwayat[-20:], start=1):
                if data ["tanggal"] != tanggal_sebelumnya:
                    print("=" * 30)
                    print("Tanggal :", data["tanggal"])
                    print("=" * 30)
                    tanggal_sebelumnya =data ["tanggal"]
                print(f"\nTransaksi ke-{i}")
                print("----------------------------")
                print ("Tanggal    :", data["tanggal"])
                print ("Jenis      :", data["jenis"])
                print ("Kategori   :", data["kategori"])
                print ("Keterangan :", data["keterangan"])
                print("Nominal    :",format_rupiah(data["nominal"]))
        elif pilihan_riwayat == "2":
            tanggal = input("Masukan tanggal(ddmmyyyy): ")
            if len(tanggal) == 8 and tanggal.isdigit():
                tanggal_cari = f"{tanggal[:2]}/{tanggal[2:4]}/{tanggal[4:]}"
            else:
                print("format tanggal salah.")
                input("\nTekan Enter untuk kembali...")
                continue
            ditemukan = False
            for data in riwayat:
               if data["tanggal"] == tanggal_cari:
                ditemukan = True
                print("="*30)
                print("Tanggal    :",data["tanggal"])
                print("Jenis      :",data["jenis"])
                print("Kategori   :",data["kategori"])
                print("Keterangan :",data["keterangan"])
                print("Nominal    :",format_rupiah(data["nominal"]))
            if not ditemukan:
                 print("Tidak ada transaksi")
        elif pilihan_riwayat == "3":
            bulan = input ("Masukan bulan (01-12): ")
            tahun = input ("Masukan tahun : ")
            ditemukan= False
            for data in riwayat:
                tgl = data["tanggal"].split("/")
                if tgl[1] == bulan and tgl[2] == tahun:
                   ditemukan = True
                   print("="*30)
                   print("Tanggal    :",data["tanggal"])
                   print("Jenis      :",data["jenis"])
                   print("Kategori   :",data["kategori"])
                   print("Keterangan :",data["keterangan"])
                   print("Nominal    :",format_rupiah(data["nominal"]))
            if not ditemukan:
                   print("Tidak ada transaksi dibulan tersebut")
        elif pilihan_riwayat == "4":
             tahun = input ("Masukan tahun : ")
             ditemukan = False
             for data in riwayat:
                tgl = data["tanggal"].split("/")
                if tgl[2] == tahun:
                   ditemukan = True
                   print("="*30)
                   print("Tanggal    :",data["tanggal"])
                   print("Jenis      :",data["jenis"])
                   print("Kategori   :",data["kategori"])
                   print("Keterangan :",data["keterangan"])
                   print("Nominal    :",format_rupiah(data["nominal"]))
             if not ditemukan:
                   print("Tidak ada transaksi dibulan tersebut")
        elif pilihan_riwayat == "5":
            pass
        input("\nTekan Enter untuk kembali ke menu...")
    elif pilihan == "5":
        print("===INFORMASI KEUANGAN===")
        print("Saldo saat ini    :",format_rupiah(saldo))
        if saldo < 0:
                 print("\n⚠️PERINGATAN")
                 print("Status : DEFISIT")
                 print("Saldo defisit :",format_rupiah(saldo))
        print("Total Pemasukan   :",format_rupiah(total_pemasukan))
        print("Total Pengeluaran :",format_rupiah(total_pengeluaran))
        print("Total Tabungan    :",format_rupiah(total_tabungan))
        input("\nTekan Enter untuk kembali ke menu...")
    elif pilihan == "6":
        print()
        print("===============================")
        print("=== TERIMA KASIH TELAH MENGGUNAKAN ===")
        print("     APLIKASI KEUANGAN KELUARGA DY")
        print("by.doni.p")
        print("===============================")
        break
    else:
        print("Pilihan tidak tersedia")
    
    
    
    
    

    

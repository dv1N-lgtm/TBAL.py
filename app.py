from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import calendar
from datetime import date, timedelta

app = Flask(__name__)

DATABASE = os.path.join(app.root_path, "studymate.db")


def koneksi_database():
    koneksi = sqlite3.connect(DATABASE)
    koneksi.row_factory = sqlite3.Row
    return koneksi


def buat_tabel():
    koneksi = koneksi_database()

    # Buat tabel jika belum ada
    koneksi.execute("""
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            selesai INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Periksa apakah kolom deadline sudah ada
    kolom = koneksi.execute(
        "PRAGMA table_info(tugas)"
    ).fetchall()

    nama_kolom = [item["name"] for item in kolom]

    # Tambahkan kolom tanpa menghapus tugas lama
    if "deadline" not in nama_kolom:
        koneksi.execute(
            "ALTER TABLE tugas ADD COLUMN deadline TEXT"
        )

    koneksi.commit()
    koneksi.close()


@app.route("/")
def home():
    koneksi = koneksi_database()

    daftar_tugas = koneksi.execute("""
        SELECT * FROM tugas
        ORDER BY
            CASE WHEN deadline IS NULL OR deadline = ''
            THEN 1 ELSE 0 END,
            deadline ASC,
            id DESC
    """).fetchall()

    koneksi.close()

    hari_ini = date.today()
    batas_dekat = hari_ini + timedelta(days=3)

    selected_date = request.args.get(
        "tanggal", hari_ini.isoformat()
    )

    try:
        selected_date = date.fromisoformat(selected_date)
        selected_date = selected_date.isoformat()
    except ValueError:
        selected_date = hari_ini.isoformat()

    # Menentukan bulan yang ditampilkan
    try:
        tahun = int(request.args.get("tahun", hari_ini.year))
        bulan = int(request.args.get("bulan", hari_ini.month))

        if not 1 <= bulan <= 12 or not 1 <= tahun <= 9999:
            raise ValueError

    except (ValueError, TypeError):
        tahun = hari_ini.year
        bulan = hari_ini.month

    # Membuat susunan minggu kalender
    kalender = calendar.Calendar(firstweekday=6)
    minggu = kalender.monthdayscalendar(tahun, bulan)

    # Mengumpulkan tugas berdasarkan tanggal deadline
    tugas_per_tanggal = {}

    for item in daftar_tugas:
        if item["deadline"]:
            tanggal = item["deadline"]

            if tanggal not in tugas_per_tanggal:
                tugas_per_tanggal[tanggal] = []

            tugas_per_tanggal[tanggal].append(item)

    # Navigasi bulan sebelumnya dan berikutnya
    bulan_sebelumnya = bulan - 1
    tahun_sebelumnya = tahun

    if bulan_sebelumnya == 0:
        bulan_sebelumnya = 12
        tahun_sebelumnya -= 1

    bulan_berikutnya = bulan + 1
    tahun_berikutnya = tahun

    if bulan_berikutnya == 13:
        bulan_berikutnya = 1
        tahun_berikutnya += 1

    return render_template(
        "index.html",
        selected_date=selected_date,
        tugas=daftar_tugas,
        today=hari_ini.isoformat(),
        soon_until=batas_dekat.isoformat(),
        kalender_bulan=calendar.month_name[bulan],
        kalender_tahun=tahun,
        kalender_minggu=minggu,
        tugas_per_tanggal=tugas_per_tanggal,
        bulan_sebelumnya=bulan_sebelumnya,
        tahun_sebelumnya=tahun_sebelumnya,
        bulan_berikutnya=bulan_berikutnya,
        tahun_berikutnya=tahun_berikutnya
    )

@app.route("/tambah", methods=["POST"])
def tambah():
    nama_tugas = request.form.get(
        "nama_tugas", ""
    ).strip()

    deadline = request.form.get(
        "deadline", ""
    ).strip()

    if nama_tugas:
        koneksi = koneksi_database()

        koneksi.execute("""
            INSERT INTO tugas (nama, deadline)
            VALUES (?, ?)
        """, (
            nama_tugas,
            deadline if deadline else None
        ))

        koneksi.commit()
        koneksi.close()

    return redirect(url_for("home"))


@app.route("/selesai/<int:id_tugas>", methods=["POST"])
def selesai(id_tugas):
    koneksi = koneksi_database()

    koneksi.execute("""
        UPDATE tugas
        SET selesai = 1 - selesai
        WHERE id = ?
    """, (id_tugas,))

    koneksi.commit()
    koneksi.close()

    return redirect(url_for("home"))


@app.route("/hapus/<int:id_tugas>", methods=["POST"])
def hapus(id_tugas):
    koneksi = koneksi_database()

    koneksi.execute(
        "DELETE FROM tugas WHERE id = ?",
        (id_tugas,)
    )

    koneksi.commit()
    koneksi.close()

    return redirect(url_for("home"))


buat_tabel()

if __name__ == "__main__":
    app.run(debug=True)
# TBAL1

Aplikasi web daftar tugas dengan deadline dan kalender.

## Jalankan secara lokal

Gunakan Python 3.12 atau lebih baru. Dari folder repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Buka <http://127.0.0.1:5000>. Secara lokal, aplikasi menggunakan SQLite dan
membuat `studymate.db` di folder project.

## Deploy ke Vercel

Vercel mendeteksi aplikasi Flask dari `requirements.txt` dan entrypoint
`app.py`; folder `public` digunakan untuk file statis.

1. Import repository ini ke Vercel dan deploy dengan pengaturan Python standar.
2. Siapkan database PostgreSQL, misalnya melalui provider PostgreSQL yang
   kompatibel.
3. Di **Project Settings → Environment Variables**, tambahkan `DATABASE_URL`
   dengan connection string PostgreSQL. Atur untuk environment yang ingin
   digunakan dan jangan commit connection string atau kredensial ke Git.
4. Deploy ulang setelah menambahkan variabel tersebut.

Aplikasi menolak berjalan di Vercel tanpa `DATABASE_URL`, karena filesystem
serverless tidak cocok untuk menyimpan database SQLite secara persisten.

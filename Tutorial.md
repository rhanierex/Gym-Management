gym-management/
├── app.py                    ✅ (Kode lengkap di atas)
├── models.py                 ✅ (Sudah ada sebelumnya)
├── requirements.txt
├── static/
│   └── style.css            ✅ (Update dengan CSS di atas)
├── templates/
│   ├── base.html            ✅ (Kode lengkap di atas)
│   ├── login.html           ✅ (Sudah ada sebelumnya)
│   ├── register_admin.html  ✅ (Sudah ada sebelumnya)
│   ├── register.html        ✅ (Sudah ada sebelumnya)
│   ├── edit.html            ✅ (Sudah ada sebelumnya)
│   ├── perpanjangan.html    ✅ (Sudah ada sebelumnya)
│   ├── delete.html          ✅ (Sudah ada sebelumnya)
│   ├── success.html         ✅ (Sudah ada sebelumnya)
│   ├── profile.html         ✅ (Sudah ada sebelumnya)
│   ├── change_password.html ✅ (Sudah ada sebelumnya)
│   ├── laporan.html         ✅ (Sudah ada sebelumnya)
│   ├── qrcode.html          ✅ (Part 2 sebelumnya)
│   ├── scan.html            ✅ (Part 2 sebelumnya)
│   ├── scan_public.html     ✅ (Part 2 sebelumnya)
│   └── attendance.html      ✅ (Part 2 sebelumnya)
└── gym.db                   (Auto-generated)


# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan aplikasi
python app.py

# 3. Akses aplikasi
# Admin Dashboard: http://127.0.0.1:5000
# Scan Public: http://127.0.0.1:5000/scan-public

# 4. Login default
# Username: admin
# Password: admin123


set TELEGRAM_BOT_TOKEN=8208613879:AAE7jXwn3L0TNpvalBmK6bdgfFOpjY1T4j0
set TELEGRAM_CHAT_ID=687703122

📱 Command Telegram Bot:
/start atau /help - Menu bantuan
/cek MG123456 - Cek info member by ID
/cari [nama] - Cari member by nama
/expired - List member akan expired (3 hari)
/aktif - List semua member aktif
/stats - Statistik gym (member aktif, expired, pendapatan)
/alert - Manual trigger alert expired




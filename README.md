# OmniScan - Web-Based QR & Barcode Scanner Engine

OmniScan adalah aplikasi pemindai (*scanner*) dan pembuat (*generator*) QR Code serta Barcode berbasis web yang dibangun menggunakan **Python (Flask)** dan **JavaScript (html5-qrcode)**. Aplikasi ini dirancang responsif, dilengkapi fitur *Dark Mode*, penyimpanan riwayat pemindaian ke database, serta ekspor data ke format CSV.

---

## 🌟 Fitur Utama

- 📸 **Real-Time Camera Scanner**: Memindai QR Code dan Barcode secara langsung lewat kamera perangkat.
- 📁 **Upload Gambar**: Membaca kode dari file gambar (PNG, JPG, WEBP) menggunakan library `pyzbar`.
- 🔗 **Navigasi & Salin Otomatis**: Mendeteksi tautan URL untuk membuka halaman web secara langsung atau menyalin teks ke *clipboard*.
- ✨ **QR Code Generator**: 
  - Mengubah Teks/URL menjadi QR Code.
  - **File to QR**: Mengunggah berkas (PDF, Gambar, dll) dan mengubahnya menjadi QR Code yang berisi link unduhan berkas tersebut.
- 📜 **Riwayat Pemindaian**: Menyimpan semua data pemindaian ke database SQLite secara otomatis.
- 📊 **Export CSV**: Mengunduh seluruh riwayat pemindaian ke file CSV/Excel.
- 🌗 **Dark Mode & Responsive UI**: Antarmuka modern berbasis Bootstrap 5 dengan toggle tema Terang/Gelap dan responsif di smartphone maupun desktop.
- 🔊 **Feedback Suara & Visual**: Efek suara *beep* (via Web Audio API) dan animasi bingkai saat pemindaian berhasil.

---

## 🛠️ Teknologi yang Digunakan

* **Backend**: Python 3, Flask, Flask-SQLAlchemy, Pyzbar, Pillow, Qrcode
* **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, FontAwesome 6
* **Library Scan Kamera**: `html5-qrcode`
* **Database**: SQLite

---

## 📂 Struktur Proyek

```text
OmniScan/
│
├── app.py                  # File utama aplikasi (Routing & Logika Backend)
├── config.py               # Konfigurasi aplikasi (Database URI, path folder upload)
├── requirements.txt        # Daftar library Python (Flask, qrcode, pyzbar, SQLAlchemy, dll)
│
├── instance/               # Folder (terbuat otomatis) untuk menyimpan database
│   └── omniscan.db         # Database SQLite untuk menyimpan riwayat scan
│
├── static/                 # Folder untuk aset publik
│   ├── css/
│   │   └── style.css       # Styling kustom, UI responsif, & variabel Dark Mode
│   ├── js/
│   │   ├── scanner.js      # Logika pemindai kamera (html5-qrcode), fitur copy & navigasi
│   │   └── main.js         # Logika global (toggle dark mode, inisiasi elemen)
│   ├── audio/
│   │   └── beep.mp3        # File suara untuk feedback saat scan berhasil
│   ├── uploads/            # Direktori penyimpanan file yang diunggah (PDF, Image, dll)
│   └── generated_qrs/      # Direktori penyimpanan sementara gambar QR Code yang dibuat
│
└── templates/              # Folder untuk file HTML (Jinja2 Templates)
    ├── base.html           # Template induk (Navbar, Footer, layout dasar)
    ├── index.html          # Halaman Beranda (Menu utama)
    ├── scan.html           # Halaman Scanner (Tab Kamera & Tab Upload Gambar)
    ├── generate.html       # Halaman QR Generator (Tab Teks/URL & Tab Upload File)
    └── history.html        # Halaman Riwayat Scan dengan tombol Export CSV


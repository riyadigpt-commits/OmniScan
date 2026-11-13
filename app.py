import os
import csv
from io import StringIO
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, Response, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

# ==========================================
# 1. KONFIGURASI APLIKASI
# ==========================================
app = Flask(__name__)

# Konfigurasi direktori penyimpanan
BASE_DIR = os.path.abspath(os.path.dirname(__name__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
QR_FOLDER = os.path.join(BASE_DIR, 'static', 'generated_qrs')

# Pastikan folder tersedia
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Maksimal file 16MB

# Konfigurasi Database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omniscan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 2. MODEL DATABASE (Tabel Histori)
# ==========================================
class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_type = db.Column(db.String(50), nullable=False) # 'QR_CODE', 'BARCODE', dll
    data_result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Inisiasi database (membuat file omniscan.db jika belum ada)
with app.app_context():
    db.create_all()

# ==========================================
# 3. ROUTING HALAMAN WEB (Frontend Views)
# ==========================================
@app.route('/')
def index():
    # Halaman Utama / Dashboard
    return render_template('index.html')

@app.route('/scan')
def scan():
    # Halaman Scanner (Kamera & Upload)
    return render_template('scan.html')

@app.route('/generate')
def generate():
    # Halaman QR Generator (Teks & File)
    return render_template('generate.html')

@app.route('/history')
def history():
    # Mengambil data histori dari database, urut dari yang terbaru
    records = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).all()
    return render_template('history.html', records=records)

# ==========================================
# 4. ROUTING API (Logika Backend)
# ==========================================

# Endpoint: Menyimpan hasil scan dari kamera (Frontend JS -> Backend DB)
@app.route('/api/scan/save', methods=['POST'])
def save_scan():
    data = request.json
    new_scan = ScanHistory(
        scan_type=data.get('scan_type', 'UNKNOWN'),
        data_result=data.get('data_result', '')
    )
    db.session.add(new_scan)
    db.session.commit()
    return jsonify({"status": "success", "message": "Scan tersimpan!"})

# Endpoint: Membaca QR/Barcode dari gambar yang diunggah
@app.route('/api/scan/upload', methods=['POST'])
def scan_upload():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "File kosong"}), 400

    if file:
        # Baca gambar menggunakan Pillow
        img = Image.open(file.stream)
        # Decode gambar menggunakan pyzbar
        decoded_objects = decode(img)
        
        if not decoded_objects:
            return jsonify({"status": "error", "message": "QR/Barcode tidak ditemukan pada gambar."})

        # Ambil hasil pertama
        result_data = decoded_objects[0].data.decode('utf-8')
        code_type = decoded_objects[0].type

        # Simpan ke histori
        new_scan = ScanHistory(scan_type=code_type, data_result=result_data)
        db.session.add(new_scan)
        db.session.commit()

        return jsonify({
            "status": "success", 
            "data_result": result_data, 
            "scan_type": code_type
        })

# Endpoint: Generate QR Code dari Teks/URL
@app.route('/api/generate/text', methods=['POST'])
def generate_text_qr():
    text_data = request.form.get('text_data')
    if not text_data:
         return jsonify({"status": "error", "message": "Data teks kosong."}), 400
    
    # Membuat QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(text_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Simpan gambar sementara
    filename = f"qr_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    filepath = os.path.join(app.config['QR_FOLDER'], filename)
    img.save(filepath)
    
    # Kembalikan URL gambar agar bisa ditampilkan di frontend
    qr_url = url_for('static', filename=f'generated_qrs/{filename}')
    return jsonify({"status": "success", "qr_url": qr_url})

# Endpoint: Export histori ke CSV
@app.route('/api/history/export')
def export_history():
    records = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).all()
    
    # Generate CSV in memory
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Waktu', 'Tipe', 'Data'])
    for r in records:
         # Menyesuaikan zona waktu atau format jika perlu
         waktu = r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
         cw.writerow([r.id, waktu, r.scan_type, r.data_result])
         
    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=omniscan_history.csv"}
    )

# Endpoint: Generate QR Code dari Unggah Berkas
@app.route('/api/generate/file', methods=['POST'])
def generate_file_qr():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada berkas yang diunggah."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Berkas kosong."}), 400

    if file:
        filename = secure_filename(file.filename)
        # Memberi penamaan unik menggunakan timestamp
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Membuat URL unduh lengkap untuk berkas yang diunggah
        file_url = request.host_url.rstrip('/') + url_for('static', filename=f'uploads/{unique_filename}')

        # Membuat QR Code dari URL berkas tersebut
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(file_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        qr_filename = f"qr_file_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        qr_filepath = os.path.join(app.config['QR_FOLDER'], qr_filename)
        img.save(qr_filepath)

        qr_url = url_for('static', filename=f'generated_qrs/{qr_filename}')
        return jsonify({"status": "success", "qr_url": qr_url})

if __name__ == '__main__':
    # Jalankan di port 5000 dengan mode debug aktif untuk masa development
    app.run(debug=True, host='0.0.0.0', port=5000)
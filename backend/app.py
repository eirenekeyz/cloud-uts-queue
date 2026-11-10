import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_DIR = '/var/lib/backend_data'
DATA_FILE = os.path.join(DATA_DIR, 'queue.json')

LOKET_CONFIG = {
    "Legalisir Transkrip / Ijazah": {"prefix": "A", "loket": "Loket A - Legalisir"},
    "Surat Keterangan Mahasiswa": {"prefix": "A", "loket": "Loket A - Surat Ket."},
    "Pengajuan Beasiswa": {"prefix": "B", "loket": "Loket B - Beasiswa"},
    "Bimbingan Konseling Mahasiswa": {"prefix": "C", "loket": "Loket C - Konseling"},
    "Konsultasi Akademik / KRS": {"prefix": "D", "loket": "Loket D - Akademik & KRS"}
}

def load_queue():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_queue(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/queue', methods=['GET'])
def get_queue():
    data = load_queue()
    return jsonify(data), 200

@app.route('/queue', methods=['POST'])
def add_queue():
    try:
        req_data = request.get_json()
        if not req_data or 'student_name' not in req_data:
            return jsonify({"error": "Nama mahasiswa wajib diisi"}), 400
        
        service_type = req_data.get('service_type', 'Legalisir Transkrip / Ijazah')
        config = LOKET_CONFIG.get(service_type, {"prefix": "A", "loket": "Loket A - Layanan"})
        prefix = config["prefix"]
        loket_name = config["loket"]
        
        data = load_queue()
        
        # Konversi ke string agar aman dari data lama
        existing_numbers = []
        for item in data:
            q_num = str(item.get("queue_number", ""))
            if q_num.startswith(prefix):
                existing_numbers.append(q_num)
        
        max_num = 0
        for num_str in existing_numbers:
            try:
                num_val = int(num_str[1:])
                if num_val > max_num:
                    max_num = num_val
            except ValueError:
                pass
                
        queue_number = f"{prefix}{(max_num + 1):03d}"
        
        queue_item = {
            "queue_number": queue_number,
            "student_name": req_data.get('student_name'),
            "service_type": service_type,
            "loket": loket_name,
            "prefix": prefix
        }
        
        data.append(queue_item)
        save_queue(data)
        return jsonify({"message": "Nomor antrean berhasil diambil", "data": queue_item}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/queue', methods=['DELETE'])
def delete_queue():
    index_param = request.args.get('index', default='0')
    if not index_param.isdigit():
        return jsonify({"error": "Parameter 'index' harus berupa angka"}), 400
    
    index = int(index_param)
    data = load_queue()
    
    if not data:
        return jsonify({"error": "Antrean saat ini kosong"}), 404
        
    if index < 0 or index >= len(data):
        return jsonify({"error": "Index antrean tidak ditemukan"}), 404
        
    removed_item = data.pop(index)
    save_queue(data)
    return jsonify({"message": "Antrean berhasil diproses/selesai", "data": removed_item}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
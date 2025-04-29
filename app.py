from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime
from script.weigher_process_log import log_process

app = Flask(__name__)

    
@app.route('/weigher/upload_log_weigher', methods=['POST'])
def upload_file():
    try:
        # Jika terjadi double data: kiri json dibawah
        # return jsonify({'status': 'success'}), 200
        
        # Print debug information
        print("Content-Type:", request.headers.get('Content-Type'))
        print("Files:", request.files)
        print("Data received:", len(request.get_data()))
        
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("No filename")
            return jsonify({'error': 'No selected file'}), 400
        
        getFileName = file.filename
        filename_without_ext = getFileName.split('.')[0]
        
        # Create timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_without_ext}_{timestamp}.txt"
        
        # Save the file
        dateToday = datetime.now().strftime("%Y%m%d")
        os.makedirs(os.path.join('uploads', dateToday, filename_without_ext[-2:]), exist_ok=True)
        save_path = os.path.join('uploads', dateToday, filename_without_ext[-2:], filename)
        
        # Simpan file
        file.save(save_path)
        file_size = os.path.getsize(save_path)
        
        # Hitung jumlah baris secara cepat (tanpa memuat seluruh file ke memori)
        jumlah_baris = 0
        with open(save_path, 'r') as f:
            for _ in f:
                jumlah_baris += 1
        
        if jumlah_baris == 0:
            return jsonify({'status': 'failed', 'data': jumlah_baris}), 500
        
        # Kirim respons cepat tanpa menunggu log_process selesai
        response = {
            'status': 'success',
            'filename': filename,
            'size': file_size,
            'save_path': save_path,
            'jumlah_data': jumlah_baris
        }
        
        # Print the response dictionary
        print("Response JSON:", response)
        
        # Jalankan log_process di thread terpisah
        def process_log_async():
            try:
                log_process(save_path)
                print(f"Async log processing completed for: {save_path}")
            except Exception as e:
                print(f"Error in async log processing: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Mulai proses di background
        import threading
        thread = threading.Thread(target=process_log_async)
        thread.daemon = True
        thread.start()
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
@app.route('/iot', methods=['GET'])
def iot():
    return render_template('dashboard.html')


if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)

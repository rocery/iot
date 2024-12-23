from flask import Flask, request, jsonify
import os
from datetime import datetime
from script.weigher_process_log import log_process, get_baris

app = Flask(__name__)

@app.route('/weigher/upload_log_weigher', methods=['POST'])
def upload_file():
    try:
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
        file.save(save_path)
        
        dataCount = 0
        with open(save_path, 'r') as file:
            dataCount = file.readlines()
        if len(dataCount) == 0:
            return jsonify({'status': 'failed',
                            'data': len(dataCount)}), 500
        
        jumlah_baris = log_process(save_path)
        
        # Verify file save
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"File saved: {filename}, Size: {file_size} bytes")
            
            # Optional: Verify file content
            try:
                with open(save_path, 'r') as f:
                    first_line = f.readline().strip()
                    print(f"First line of file: {first_line}")
            except Exception as read_error:
                print(f"Error reading file: {read_error}")
            
            return jsonify({
                'status': 'success', 
                'filename': filename, 
                'size': file_size,
                'save_path': save_path,
                'jumlah_data': jumlah_baris
            }), 200
        else:
            print(f"File save failed: {save_path}")
            return jsonify({'status': 'failed'}), 500
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)

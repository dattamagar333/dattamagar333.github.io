import os
import fitz  # PyMuPDF
import json
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create upload and output directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text_data = []

        # Initial system message
        text_data.append({"role": "system", "content": "PDF Text Extraction"})

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            text_data.append({
                "role": "page", 
                "page_number": page_num + 1, 
                "content": text
            })

        return text_data
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        raise

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        try:
            text_data = extract_text(pdf_path)
            
            # Generate output filename
            output_filename = f"{os.path.splitext(filename)[0]}_extracted.jsonl"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Save text data to JSONL file
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in text_data:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')
            
            return send_file(output_path, as_attachment=True)
        
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
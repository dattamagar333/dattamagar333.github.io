import os
import fitz  # PyMuPDF
import json
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.ERROR, filename='pdf_data_extractor.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text_data = []

    # Initial system message
    text_data.append({"role": "system", "content": "You are a helpful AI assistant."})

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_data.append({"role": "assistant", "content": f"Page {page_num + 1}:\n{text}"})

    return text_data

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
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
            logging.error(f"Error processing PDF {pdf_path}: {e}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
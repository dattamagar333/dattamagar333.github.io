# PDF Text Extractor

## Description
A web application to extract text from PDF files and convert them to JSONL format.

## Prerequisites
- Python 3.8+
- pip

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/pdf-text-extractor.git
cd pdf-text-extractor
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the backend
```bash
python backend/app.py
```

2. Open `frontend/index.html` in your browser

## Features
- Upload PDF files
- Extract text from PDFs
- Download extracted text as JSONL file

## Technologies
- Flask (Backend)
- PyMuPDF (PDF Processing)
- HTML/CSS/JavaScript (Frontend)
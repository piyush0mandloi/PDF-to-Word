from flask import Flask, request, render_template, send_file
import os
import fitz
import aspose.words as aw
from transformers import pipeline


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

summarizer = pipeline('summarization', model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''.join([page.get_text() for page in doc])
    return text if text.strip() else "No text found in the PDF."

def summarize_text(text):
    if len(text) < 100:
        return "Text is too short to summarize."
    
    summary = summarizer(text, max_length=200, min_length = 50, do_sample=False)
    return summary[0]['summary_text']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdfFile' not in request.files:
        return 'No file part'
    
    file = request.files['pdfFile']
    if file.filename == '':
        return 'No selected file'
    
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        try:
            word_path = os.path.join(OUTPUT_FOLDER, file.filename.replace('.pdf', '.docx'))
            doc = aw.Document(pdf_path)
            doc.save(word_path)

            extracted_text = extract_text_from_pdf(pdf_path)
            summary = summarize_text(extracted_text)

            return render_template("result.html", summary=summary, word_file=file.filename.replace('.pdf', '.docx'))
        except Exception as e:
            return f"Error during conversion: {str(e)}", 500
    else:
        return f"Error: Only pds files are allowed", 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
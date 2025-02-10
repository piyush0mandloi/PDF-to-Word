from flask import Flask, request, render_template, send_file
import os
import aspose.words as aw

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


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

            return send_file(word_path, as_attachment=True)
        except Exception as e:
            return f"Error during conversion: {str(e)}", 500
    else:
        return f"Error: Only pds files are allowed", 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
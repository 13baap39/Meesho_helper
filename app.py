import os
import shutil
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from utils.pdf_parser import extract_customer_names
from utils.leaflet_maker import generate_leaflet_pdf

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'}

# --- Flask App Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['SECRET_KEY'] = 'super_secret_key'  # For flash messages

# --- Ensure Folders Exist ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# --- Helper Function ---
def allowed_file(filename):
    """Check if uploaded file has a valid PDF extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/', methods=['GET'])
def upload_form():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'pdf_file' not in request.files:
        flash('No file uploaded.')
        return redirect(url_for('upload_form'))

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('upload_form'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)

        # Extract names
        customer_names = extract_customer_names(uploaded_path)
        if not customer_names:
            flash('No customer names found in the PDF.')
            return redirect(url_for('upload_form'))

        # Generate personalized leaflet
        output_filename = f"leaflet_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        generate_leaflet_pdf(customer_names, output_path) 

        return render_template('index.html', generated_filename=output_filename)

    else:
        flash('Invalid file type. Please upload a PDF.')
        return redirect(url_for('upload_form'))

@app.route('/download/<filename>')
def download_file(filename):
    """Serves the generated PDF file for download."""
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

# --- Main Entry ---
if __name__ == '__main__':
    app.run(debug=True)
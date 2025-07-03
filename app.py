import os
import shutil
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Import your existing utilities
from utils.pdf_parser import extract_customer_names
from utils.leaflet_maker import generate_leaflet_pdf

# Import the new bill combiner utility
from utils.bill_combiner import crop_and_arrange_bills

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
    """Renders the main upload form, defaulting to leaflet generation tab."""
    # The 'feature' context variable is used by index.html to decide which tab to show active
    return render_template('index.html', feature='leaflet')

@app.route('/process_leaflets', methods=['POST'])
def process_leaflets_file():
    """Handles PDF upload and generates leaflets."""
    if 'pdf_file' not in request.files:
        flash('No file uploaded for leaflet generation.', 'error')
        return redirect(url_for('upload_form'))

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No file selected for leaflet generation.', 'error')
        return redirect(url_for('upload_form'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)

        # Extract names
        customer_names = extract_customer_names(uploaded_path)
        if not customer_names:
            flash('No customer names found in the PDF for leaflet generation.', 'error')
            return redirect(url_for('upload_form'))

        # Generate personalized leaflet
        output_filename = f"leaflet_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        try:
            generate_leaflet_pdf(customer_names, output_path)
            flash('Leaflets generated successfully!', 'success')
            return render_template('index.html', generated_filename=output_filename, feature='leaflet')
        except Exception as e:
            flash(f'Error generating leaflets: {e}', 'error')
            return redirect(url_for('upload_form'))
    else:
        flash('Invalid file type. Please upload a PDF for leaflet generation.', 'error')
        return redirect(url_for('upload_form'))


@app.route('/process_combined_bills', methods=['POST'])
def process_combined_bills_file():
    """Handles PDF upload and generates 4-up combined bills."""
    if 'pdf_file' not in request.files:
        flash('No file uploaded for bill cropping.', 'error')
        # Pass feature='cropper' to ensure the cropper tab stays active on redirect
        return redirect(url_for('upload_form', feature='cropper')) 

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No file selected for bill cropping.', 'error')
        return redirect(url_for('upload_form', feature='cropper'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)

        # Generate combined bills PDF (4 per A4 page)
        output_filename = f"cropped_bills_4up_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        try:
            crop_and_arrange_bills(uploaded_path, output_path)
            flash('Bills cropped and combined successfully!', 'success')
            return render_template('index.html', generated_cropped_filename=output_filename, feature='cropper')
        except Exception as e:
            flash(f'Error during bill cropping: {e}', 'error')
            return redirect(url_for('upload_form', feature='cropper'))
    else:
        flash('Invalid file type. Please upload a PDF for bill cropping.', 'error')
        return redirect(url_for('upload_form', feature='cropper'))

@app.route('/download/<filename>')
def download_file(filename):
    """Serves the generated PDF file for download."""
    # Ensure the file exists before attempting to send it
    full_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
    if not os.path.exists(full_path):
        flash('The requested file was not found.', 'error')
        return redirect(url_for('upload_form')) # Redirect to default form if file not found
        
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

# --- Main Entry ---
if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production

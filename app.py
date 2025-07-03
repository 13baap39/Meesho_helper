import os
import shutil
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Import your existing utilities
from utils.pdf_parser import extract_customer_names # Still used for leaflet and potentially hybrid bill names
from utils.leaflet_maker import generate_leaflet_pdf # Remains unchanged, used by its dedicated route
from utils.bill_combiner import crop_and_arrange_bills # Remains unchanged, used by its dedicated route

# Import the new hybrid bill generator utility
from utils.hybrid_bill_generator import generate_hybrid_bill

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'} # Only PDF files are allowed for upload

# --- Flask App Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['SECRET_KEY'] = 'super_secret_key'  # Necessary for Flask's flash messaging system

# --- Ensure Folders Exist ---
# Create the necessary directories if they don't already exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# --- Helper Function ---
def allowed_file(filename):
    """
    Checks if an uploaded file has a permitted file extension.
    Currently, only PDF files are allowed.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/', methods=['GET'])
def upload_form():
    """
    Renders the main upload form page.
    It can receive a 'feature' argument from redirects to set the active tab.
    Defaults to showing the 'leaflet' tab.
    """
    # The 'feature' context variable is used by index.html to decide which tab to show active
    requested_feature = request.args.get('feature', 'leaflet') # Default to 'leaflet'
    return render_template('index.html', feature=requested_feature)

@app.route('/process_leaflets', methods=['POST'])
def process_leaflets_file():
    """
    Handles PDF upload and triggers the leaflet generation process.
    It extracts customer names and creates personalized thank-you leaflets.
    """
    # Check if a file was actually uploaded as part of the request
    if 'pdf_file' not in request.files:
        flash('No file part in the request for leaflet generation.', 'error')
        return redirect(url_for('upload_form', feature='leaflet'))

    file = request.files['pdf_file']
    # Check if a file was selected by the user (filename is not empty)
    if file.filename == '':
        flash('No file selected for leaflet generation.', 'error')
        return redirect(url_for('upload_form', feature='leaflet'))

    # Process the file if it exists and is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) # Sanitize filename for security
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path) # Save the uploaded file temporarily

        # Extract customer names from the uploaded PDF
        customer_names = extract_customer_names(uploaded_path)
        if not customer_names:
            flash('No customer names found in the PDF. Please ensure it is a valid Meesho order label.', 'error')
            return redirect(url_for('upload_form', feature='leaflet'))

        # Define output path for the generated leaflet PDF
        output_filename = f"leaflet_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        try:
            # Call the utility function to generate the leaflet PDF
            generate_leaflet_pdf(customer_names, output_path)
            flash('Leaflets generated successfully! Click the link below to download.', 'success')
            return render_template('index.html', generated_filename=output_filename, feature='leaflet')
        except Exception as e:
            # Catch any errors during PDF generation and show a flash message
            flash(f'Error generating leaflets: {e}', 'error')
            return redirect(url_for('upload_form', feature='leaflet'))
    else:
        # Handle invalid file types
        flash('Invalid file type. Please upload a PDF for leaflet generation.', 'error')
        return redirect(url_for('upload_form', feature='leaflet'))


@app.route('/process_combined_bills', methods=['POST'])
def process_combined_bills_file():
    """
    Handles PDF upload and generates the 4-up combined bills PDF.
    It crops individual bills and arranges them on A4 pages.
    """
    if 'pdf_file' not in request.files:
        flash('No file part in the request for bill cropping.', 'error')
        return redirect(url_for('upload_form', feature='cropper')) 

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No file selected for bill cropping.', 'error')
        return redirect(url_for('upload_form', feature='cropper'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)

        # Define output path for the generated combined bills PDF
        output_filename = f"cropped_bills_4up_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        try:
            # Call the utility function to generate the 4-up cropped bills
            crop_and_arrange_bills(uploaded_path, output_path)
            flash('Bills cropped and combined successfully! Click the link below to download.', 'success')
            return render_template('index.html', generated_cropped_filename=output_filename, feature='cropper')
        except Exception as e:
            flash(f'Error during bill cropping: {e}', 'error')
            return redirect(url_for('upload_form', feature='cropper'))
    else:
        flash('Invalid file type. Please upload a PDF for bill cropping.', 'error')
        return redirect(url_for('upload_form', feature='cropper'))

@app.route('/process_hybrid_bills', methods=['POST'])
def process_hybrid_bills_file():
    """
    Handles PDF upload and generates the 'hybrid bill' PDF.
    This new feature combines cropped bills and personalized leaflets on one page.
    """
    if 'pdf_file' not in request.files:
        flash('No file part in the request for hybrid bill generation.', 'error')
        return redirect(url_for('upload_form', feature='hybrid')) 

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No file selected for hybrid bill generation.', 'error')
        return redirect(url_for('upload_form', feature='hybrid'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)

        # Define output path for the generated hybrid bill PDF
        output_filename = f"hybrid_bill_{filename}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
        
        try:
            # Call the new utility function to generate the hybrid bill
            generate_hybrid_bill(uploaded_path, output_path)
            flash('Hybrid Bills generated successfully! Click the link below to download.', 'success')
            return render_template('index.html', generated_hybrid_filename=output_filename, feature='hybrid')
        except Exception as e:
            flash(f'Error generating hybrid bills: {e}', 'error')
            return redirect(url_for('upload_form', feature='hybrid'))
    else:
        flash('Invalid file type. Please upload a PDF for hybrid bill generation.', 'error')
        return redirect(url_for('upload_form', feature='hybrid'))

@app.route('/download/<filename>')
def download_file(filename):
    """
    Serves the generated PDF file for download from the 'generated' folder.
    Includes basic error handling if the file is not found.
    """
    full_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
    if not os.path.exists(full_path):
        flash('The requested file was not found. It might have been removed or never generated.', 'error')
        return redirect(url_for('upload_form')) # Redirect to default form if file not found
        
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

# --- Main Entry Point ---
if __name__ == '__main__':
    # When running locally, set debug=True for development.
    # Set debug=False for production deployment.
    port = int(os.environ.get("PORT",5000))app.run(host="0.0.0.0", port=port)

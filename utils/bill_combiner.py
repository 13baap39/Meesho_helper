import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import io
import os

# Define standard A4 page dimensions in points (1 inch = 72 points)
PAGE_WIDTH, PAGE_HEIGHT = A4

# === CORRECTED CROP_RECT DEFINITION ===
# This rectangle defines the region to extract from the *original* PDF page.
# (x0, y0, x1, y1) where (0,0) is top-left, and Y increases downwards in PyMuPDF.
# Based on the "image of cropped bill" you provided, the desired content ends around Y=420 points from the top.
CROP_RECT = fitz.Rect(0, 0, PAGE_WIDTH, 350)
# This will extract a section of width PAGE_WIDTH (595 points) and height 420 points.
# This cropped section will contain the QR code, customer address, product details, barcode, etc.,
# but will exclude the "BILL TO / SHIP TO" block and the full financial table.

def crop_and_arrange_bills(input_pdf_path: str, output_pdf_path: str):
    """
    Takes a multi-page PDF (where each page is a full Meesho bill)
    and generates a new PDF with 4 cropped bills arranged on each A4 page.
    """
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        raise ValueError(f"Error opening input PDF '{input_pdf_path}': {e}")
    
    # Create a new PDF canvas for the output file
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    # Get dimensions of the content to be cropped from the source PDF (fixed by CROP_RECT)
    crop_original_width = CROP_RECT.width
    crop_original_height = CROP_RECT.height

    # Calculate target dimensions for each of the 4 slots on the output A4 page.
    # We need to consider margins from the A4 page edges and gutters between the cropped bills.
    page_margin = 1.0 * cm  # Margin from the outer edges of the A4 output page
    inner_gutter = 0.7 * cm # Space between the two columns and two rows of bills

    # Calculate the effective width/height available for two slots, considering margins and one gutter
    available_space_for_2_slots_width = PAGE_WIDTH - (2 * page_margin) - inner_gutter
    available_space_for_2_slots_height = PAGE_HEIGHT - (2 * page_margin) - inner_gutter

    # Determine the maximum width and height each individual slot can occupy
    slot_width = available_space_for_2_slots_width / 2
    slot_height = available_space_for_2_slots_height / 2

    # Define the (x, y) coordinates for the bottom-left corner of each of the 4 slots on the A4 output page.
    # ReportLab's Y-axis starts from the bottom of the page.
    slot_positions = [
        # Top-Left Slot
        (page_margin, page_margin + slot_height + inner_gutter),
        # Top-Right Slot
        (page_margin + slot_width + inner_gutter, page_margin + slot_height + inner_gutter),
        # Bottom-Left Slot
        (page_margin, page_margin),
        # Bottom-Right Slot
        (page_margin + slot_width + inner_gutter, page_margin),
    ]

    current_slot_index = 0 # To track which of the 4 slots we're currently filling on the output page

    # Iterate through each page of the input PDF (each page represents one full bill)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Calculate the necessary scaling factor to fit the cropped content
        # (original crop_original_width x crop_original_height) into a slot
        # (slot_width x slot_height) while maintaining aspect ratio.
        scale_factor_width = slot_width / crop_original_width
        scale_factor_height = slot_height / crop_original_height
        
        # Use the smaller scale factor to ensure the entire cropped image fits within the slot boundaries
        scale_factor = min(scale_factor_width, scale_factor_height)

        # Create a transformation matrix for PyMuPDF to render the pixmap at a good resolution.
        # Using a fixed DPI (e.g., 200 DPI) for initial rendering of the pixmap for quality.
        render_dpi = 200 # DPI for rendering the pixmap from the source PDF
        render_scale = render_dpi / 72.0 # PyMuPDF's default unit is 1/72 inch (point)

        # Get the pixmap (image representation) of the specified cropped region,
        # rendered at the calculated 'render_scale' for quality.
        # The 'clip' argument ensures only this part of the original page is processed.
        pix = page.get_pixmap(matrix=fitz.Matrix(render_scale, render_scale), clip=CROP_RECT)
        
        # Convert the PyMuPDF pixmap into an in-memory image suitable for ReportLab.
        img_buffer = io.BytesIO(pix.tobytes("png")) # PNG is lossless and generally good for text/graphics
        img = ImageReader(img_buffer)

        # Get the (x, y) position for the bottom-left corner of the current slot on the output A4 page
        x_pos_slot, y_pos_slot = slot_positions[current_slot_index]

        # Calculate the final drawing dimensions on the ReportLab canvas.
        # We want the cropped content to be scaled to `slot_width` x `slot_height` (or less if aspect ratio forces).
        # The dimensions of 'pix' are already `crop_original_width * render_scale` etc.
        # So, to get the final display size on ReportLab, we need to apply the 'scale_factor' *again*
        # (or just `pix.width / render_scale * scale_factor` but that's complex).
        # A simpler way: calculate draw_width/height based on original crop size and final scale factor.
        draw_width = crop_original_width * scale_factor
        draw_height = crop_original_height * scale_factor
        
        # Center the image within its allocated slot
        # ReportLab's drawImage takes the bottom-left corner of the image.
        draw_x = x_pos_slot + (slot_width - draw_width) / 2
        draw_y = y_pos_slot + (slot_height - draw_height) / 2

        # Draw the scaled image onto the ReportLab canvas.
        c.drawImage(img, draw_x, draw_y, width=draw_width, height=draw_height)

        current_slot_index += 1 # Move to the next slot

        # Check if 4 bills have been placed on the current output page,
        # or if this is the last bill from the input PDF (and there's at least one bill on the current page).
        if current_slot_index == 4 or (page_num == len(doc) - 1 and current_slot_index > 0):
            c.showPage() # Finalize the current page on the canvas and start a new one
            current_slot_index = 0 # Reset slot index for the next output page

    doc.close() # Close the input PDF document
    c.save() # Save the generated output PDF

# --- Test block --- (This block remains unchanged, but will now use the new CROP_RECT)
if __name__ == '__main__':
    # Ensure necessary directories exist for testing
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated", exist_ok=True) 

    test_input_pdf = os.path.join("uploads", "test_multipage_bill.pdf")
    test_output_pdf = os.path.join("generated", "combined_bills_4perpage_test.pdf")
    
    # Create a dummy multi-page PDF for testing the bill cropping logic.
    temp_doc = fitz.open()
    for i in range(10): # Create 10 dummy pages
        page = temp_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        # Add content that would typically be in the cropped region (top ~420 points)
        page.insert_text((PAGE_WIDTH / 4, 50), f"MEESHO BILL - Order {i+1}", fontsize=20, color=(0,0,0)) # Adjusted Y
        page.insert_text((PAGE_WIDTH / 4, 100), f"Customer: Lazy Man {i+1} Ji!", fontsize=14, color=(0,0,0)) # Adjusted Y
        page.insert_text((PAGE_WIDTH / 4, 150), f"Product: Stylish Scarf {i+1}", fontsize=10, color=(0,0,0)) # Adjusted Y
        page.insert_text((PAGE_WIDTH / 4, 200), f"Order No: 1234567890{i+1}", fontsize=9, color=(0,0,0)) # Adjusted Y
        # Simulate content that would typically be in the *excluded* region (financial details, below Y=420)
        page.insert_text((PAGE_WIDTH / 4, 450), f"Tax Invoice Details: (will be cropped)", fontsize=10, color=(0.5, 0.5, 0.5)) # Adjusted Y
        page.insert_text((PAGE_WIDTH / 4, 700), f"Financial Total: Rs. {150 + i*5}.00 (will be cropped)", fontsize=10, color=(0.5, 0.5, 0.5)) # Adjusted Y
        # Draw a rectangle to visualize the full page boundaries
        page.draw_rect(fitz.Rect(20, 20, PAGE_WIDTH - 20, PAGE_HEIGHT - 20), width=0.5)

    temp_doc.save(test_input_pdf)
    temp_doc.close()
    print(f"Created dummy input PDF for testing: {test_input_pdf}")

    try:
        # Run the bill cropping function with the dummy input
        crop_and_arrange_bills(test_input_pdf, test_output_pdf)
        print(f"Generated combined PDF for testing: {os.path.abspath(test_output_pdf)}")
    except ValueError as e:
        print(f"Test failed: {e}")

import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import io
import os

# Define standard A4 page dimensions in points (1 inch = 72 points)
PAGE_WIDTH, PAGE_HEIGHT = A4

# Define the cropping region for a single Meesho label on the original PDF page.
# This region aims to capture the shipping label part (QR code, customer address, product details),
# excluding the detailed financial table at the bottom.
# Based on typical Meesho bill layouts on an A4 page (595x842 points):
# We'll crop from y=180 points from the bottom of the page up to the top.
# This captures approximately the top (842 - 180) = 662 points height of the page.
CROP_RECT = fitz.Rect(0, 180, PAGE_WIDTH, PAGE_HEIGHT)

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

    # Get dimensions of the content after cropping from the source PDF
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

        # Create a transformation matrix for PyMuPDF to render the pixmap at the desired scale.
        # Multiplying by 2 for higher quality (rendering at 2x the final display resolution)
        matrix = fitz.Matrix(scale_factor * 2, scale_factor * 2) 

        # Get the pixmap (image representation) of the specified cropped region,
        # rendered at the calculated scale.
        # The 'clip' argument ensures only this part of the original page is processed.
        pix = page.get_pixmap(matrix=matrix, clip=CROP_RECT)
        
        # Convert the PyMuPDF pixmap into an in-memory image format (PNG)
        # that ReportLab's ImageReader can use.
        img_buffer = io.BytesIO(pix.tobytes("png")) 
        img = ImageReader(img_buffer)

        # Get the (x, y) position for the bottom-left corner of the current slot on the output A4 page
        x_pos_slot, y_pos_slot = slot_positions[current_slot_index]

        # Calculate the exact center position within the current slot to draw the image.
        # This helps in consistent alignment, especially if the scaled image doesn't perfectly fill the slot.
        draw_x = x_pos_slot + (slot_width - pix.width / 2) / 2 # pix.width is already scaled by `scale_factor * 2`, divide by 2 to get actual display width
        draw_y = y_pos_slot + (slot_height - pix.height / 2) / 2 # Same for height

        # Draw the image onto the ReportLab canvas.
        # We pass pix.width/2 and pix.height/2 as dimensions because pix.width/height contain the 2x resolution
        # So divide by 2 to get the actual display dimensions on the ReportLab canvas
        c.drawImage(img, draw_x, draw_y, width=pix.width / 2, height=pix.height / 2)

        current_slot_index += 1 # Move to the next slot

        # Check if 4 bills have been placed on the current output page,
        # or if this is the last bill from the input PDF (and there's at least one bill on the current page).
        if current_slot_index == 4 or (page_num == len(doc) - 1 and current_slot_index > 0):
            c.showPage() # Finalize the current page on the canvas and start a new one
            current_slot_index = 0 # Reset slot index for the next output page

    doc.close() # Close the input PDF document
    c.save() # Save the generated output PDF
    # The print statement is removed for cleaner integration with the web app,
    # as Flask's flash messages will handle user feedback.

# --- Test block ---
if __name__ == '__main__':
    # Ensure necessary directories exist for testing
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated", exist_ok=True) 

    test_input_pdf = os.path.join("uploads", "test_multipage_bill.pdf")
    test_output_pdf = os.path.join("generated", "combined_bills_4perpage_test.pdf")
    
    # Create a dummy multi-page PDF for testing the bill cropping logic.
    # This simulates a Meesho bill with 10 pages (each page being a full bill).
    temp_doc = fitz.open()
    for i in range(10): # Create 10 dummy pages
        page = temp_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        # Add content that would typically be in the cropped region
        page.insert_text((PAGE_WIDTH / 4, PAGE_HEIGHT - 100), f"MEESHO BILL - Order {i+1}", fontsize=20, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, PAGE_HEIGHT - 150), f"Customer: Lazy Man {i+1} Ji!", fontsize=14, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, PAGE_HEIGHT - 200), f"Product: Stylish Scarf {i+1}", fontsize=10, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, PAGE_HEIGHT - 250), f"Order No: 1234567890{i+1}", fontsize=9, color=(0,0,0))
        # Add content that would typically be in the *excluded* region (financial details)
        page.insert_text((PAGE_WIDTH / 4, 100), f"Total: Rs. {150 + i*5}.00 (will be cropped)", fontsize=10, color=(0.5, 0.5, 0.5))
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

    # You can uncomment the lines below to clean up the test files after running
    # os.remove(test_input_pdf)
    # os.remove(test_output_pdf)

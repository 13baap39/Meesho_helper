import fitz  # PyMuPDF for PDF parsing and image rendering
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
import re  # For name extraction

PAGE_WIDTH, PAGE_HEIGHT = A4
CROP_RECT = fitz.Rect(0, 0, PAGE_WIDTH, 350)  # Top 350 points from each PDF page

def _register_fonts_for_leaflet_draw():
    """
    Registers a font that supports emojis on Windows.
    Falls back to a default font if not found.
    """
    # This is the path to the standard emoji font on most Windows systems.
    font_path = r"C:\Windows\Fonts\seguiemj.ttf"
    font_name = "SegoeUIEmoji"
    
    try:
        if os.path.exists(font_path):
            # Register the Segoe UI Emoji font with reportlab
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return font_name
        else:
            # If the font isn't found, print a message and use a default.
            print(f"Font not found at '{font_path}'. Falling back to Helvetica.")
            return "Helvetica"
    except Exception as e:
        print(f"Error loading font: {e}. Using default font 'Helvetica'.")
        return "Helvetica"

def _draw_single_leaflet(c_obj, name: str, x_pos: float, y_pos: float, width: float, height: float):
    """Draws a single leaflet with the customer's name and a thank you message."""
    # Get the name of the best available font (with emoji support if possible)
    font = _register_fonts_for_leaflet_draw()
    
    # Draw a dashed rectangle border for the leaflet
    c_obj.setDash(1, 2)
    c_obj.rect(x_pos, y_pos, width, height)
    c_obj.setDash([], 0)

    # Begin a new text object for the leaflet content
    text_obj = c_obj.beginText()
    text_obj.setFont(font, 10)  # Use the registered font
    text_obj.setLeading(12)     # Set line spacing

    # Set the starting position for the text inside the leaflet
    text_x_start = x_pos + 0.5 * cm
    text_y_start = y_pos + height - 1.0 * cm
    text_obj.setTextOrigin(text_x_start, text_y_start)

    # The thank you message content
    text_obj.textLine(f"Thank you {name} ji!")
    text_obj.textLine("Thank you for your order — it truly means a lot to us!")
    text_obj.textLine("We hope you love your stole.")
    text_obj.textLine("If you're happy with your purchase")
    text_obj.textLine("we’d be thrilled if you could leave us a ")
    text_obj.textLine("5-star review ⭐⭐⭐⭐⭐") # This line requires emoji support
    text_obj.textLine("In case there’s anything you’re not satisfied with,")
    text_obj.textLine("please reach out to us directly on ")
    text_obj.textLine("WhatsApp: +91 7860861434")
    text_obj.textLine("we’ll do our best to make it right.")
    text_obj.textLine("Your feedback helps us improve, and your support ")
    text_obj.textLine("means the world to our small business.")
    text_obj.textLine("Thank you once again!")
    text_obj.textLine("Warm regards,")
    text_obj.textLine("  ")
    text_obj.textLine("Team Mary Creations.")

    # Draw the text object to the canvas
    c_obj.drawText(text_obj)

def _extract_name_from_page_text(page_text: str) -> str:
    """Extracts the customer's name from the text of a bill page."""
    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        if "CUSTOMER ADDRESS" in line.upper():
            if i + 1 < len(lines):
                raw_name = lines[i + 1].strip()
                if not raw_name or raw_name.isdigit():
                    return ""
                # Clean up the name string
                raw_name = re.split(r'[,-]', raw_name)[0]
                raw_name = re.sub(r'\d+', '', raw_name)
                words = raw_name.strip().split()
                # Return the first one or two words as the name
                if len(words) >= 2:
                    return " ".join(words[:2])
                elif len(words) == 1:
                    return words[0]
    return ""

def generate_hybrid_bill(input_pdf_path: str, output_pdf_path: str):
    """
    Generates a hybrid PDF with cropped bill images and thank you leaflets.
    Arranges 4 bills and 4 leaflets per page.
    """
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        raise ValueError(f"Error opening input PDF '{input_pdf_path}': {e}")
    
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    # --- Layout Calculations ---
    crop_original_width = CROP_RECT.width
    crop_original_height = CROP_RECT.height

    page_outer_margin = 1.0 * cm
    inner_gutter = 0.7 * cm

    available_width_for_2_cols = PAGE_WIDTH - (2 * page_outer_margin) - inner_gutter
    bill_slot_width = available_width_for_2_cols / 2
    scale_factor_for_bill = bill_slot_width / crop_original_width
    bill_display_height = crop_original_height * scale_factor_for_bill

    y_top_row_bill = PAGE_HEIGHT - page_outer_margin - bill_display_height
    y_bottom_row_bill = page_outer_margin
    central_leaflet_area_height = y_top_row_bill - (y_bottom_row_bill + bill_display_height + inner_gutter)

    leaflet_slot_width = bill_slot_width
    leaflet_slot_height = (central_leaflet_area_height - inner_gutter) / 2

    # Define positions for the 4 bill slots on the page
    bill_slot_positions = [
        (page_outer_margin, y_top_row_bill),
        (page_outer_margin + bill_slot_width + inner_gutter, y_top_row_bill),
        (page_outer_margin, y_bottom_row_bill),
        (page_outer_margin + bill_slot_width + inner_gutter, y_bottom_row_bill)
    ]

    y_leaflet_top_row = y_bottom_row_bill + bill_display_height + inner_gutter + leaflet_slot_height + inner_gutter
    y_leaflet_bottom_row = y_bottom_row_bill + bill_display_height + inner_gutter

    # Define positions for the 4 leaflet slots on the page
    leaflet_positions = [
        (page_outer_margin, y_leaflet_top_row),
        (page_outer_margin + leaflet_slot_width + inner_gutter, y_leaflet_top_row),
        (page_outer_margin, y_leaflet_bottom_row),
        (page_outer_margin + leaflet_slot_width + inner_gutter, y_leaflet_bottom_row)
    ]
    
    current_item_index_on_page = 0
    all_customer_names = []

    # First pass: extract all names from the PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()
        name = _extract_name_from_page_text(page_text)
        all_customer_names.append(name if name else f"Customer {page_num + 1}")

    # Second pass: generate the output PDF pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Render the cropped bill area to a high-res image
        render_dpi = 200 
        render_scale = render_dpi / 72.0 
        pix = page.get_pixmap(matrix=fitz.Matrix(render_scale, render_scale), clip=CROP_RECT)
        img_buffer = io.BytesIO(pix.tobytes("png")) 
        img = ImageReader(img_buffer)

        # Get the position for the current bill image
        x_bill_pos, y_bill_pos = bill_slot_positions[current_item_index_on_page]
        
        # Draw the bill image onto the canvas
        c.drawImage(img, x_bill_pos, y_bill_pos, width=bill_slot_width, height=bill_display_height)

        # Get the customer name and draw the corresponding leaflet
        customer_name = all_customer_names[page_num]
        x_leaflet_pos, y_leaflet_pos = leaflet_positions[current_item_index_on_page]
        _draw_single_leaflet(c, customer_name, x_leaflet_pos, y_leaflet_pos, leaflet_slot_width, leaflet_slot_height)

        current_item_index_on_page += 1
        # If the page is full (4 items) or it's the last item, save the page
        if current_item_index_on_page == 4 or (page_num == len(doc) - 1 and current_item_index_on_page > 0):
            c.showPage()
            current_item_index_on_page = 0

    doc.close()
    c.save()

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated", exist_ok=True)

    # Define paths for test files
    test_input_pdf = os.path.join("uploads", "test_multipage_bill.pdf")
    test_output_pdf = os.path.join("generated", "hybrid_bills_test_output.pdf")

    # --- Create a dummy PDF for testing purposes ---
    temp_doc = fitz.open()
    for i in range(10):
        page = temp_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        page.insert_text((PAGE_WIDTH / 4, 50), f"MEESHO BILL - Order {i+1}", fontsize=20)
        page.insert_text((PAGE_WIDTH / 4, 100), f"CUSTOMER ADDRESS", fontsize=12)
        page.insert_text((PAGE_WIDTH / 4, 120), f"Hybrid User {i+1}", fontsize=12)
        page.insert_text((PAGE_WIDTH / 4, 150), f"Product: Test Item {i+1}", fontsize=10)
    temp_doc.save(test_input_pdf)
    temp_doc.close()
    # --- End of dummy PDF creation ---

    try:
        # Run the main function
        generate_hybrid_bill(test_input_pdf, test_output_pdf)
        print(f"Successfully generated hybrid PDF: {os.path.abspath(test_output_pdf)}")
    except ValueError as e:
        print(f"Error: {e}")


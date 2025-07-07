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

# --- Constants and Configuration ---
PAGE_WIDTH, PAGE_HEIGHT = A4

# Crop region for the bill part (from original PDF page)
# Based on user's last confirmed successful cropping: top 350 points from top-left (0,0)
CROP_RECT = fitz.Rect(0, 0, PAGE_WIDTH, 350) 

# --- Duplicated Leaflet Drawing Logic (from leaflet_maker.py, adapted for single draw) ---
# Register emoji-capable font
# Note: This is a duplicated part to avoid modifying leaflet_maker.py
def _register_fonts_for_leaflet_draw():
    # Attempt to use a system emoji font if available, otherwise fall back to Helvetica
    emoji_font = "Helvetica"
    try:
        # Windows specific font path
        emoji_path = "C:/Windows/Fonts/seguiemj.ttf"
        if os.path.exists(emoji_path):
            pdfmetrics.registerFont(TTFont("EmojiFont", emoji_path))
            emoji_font = "EmojiFont"
        # Add common Linux font path if needed for deployment
        # elif os.path.exists("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"):
        #     pdfmetrics.registerFont(TTFont("EmojiFont", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"))
        #     emoji_font = "EmojiFont"
    except Exception as e:
        print(f"Warning: Could not register emoji font for hybrid bill: {e}. Falling back to Helvetica.")
    return emoji_font

# Duplicated and adapted leaflet drawing logic
def _draw_single_leaflet(c_obj, name: str, x_pos: float, y_pos: float, width: float, height: float):
    """
    Draws a single personalized leaflet onto a given ReportLab canvas object.
    This logic is adapted from leaflet_maker.py to draw to a specific area.
    """
    font = _register_fonts_for_leaflet_draw() # Register font each time (or once globally)
    
    # Draw border for the leaflet
    c_obj.setDash(1, 2) # Dashed line for cutting
    c_obj.rect(x_pos, y_pos, width, height)
    c_obj.setDash([], 0) # Reset to solid line

    # Text content (adapted from leaflet_maker.py)
    text_obj = c_obj.beginText()
    text_obj.setFont(font, 9)
    text_obj.setLeading(10.2)
    
    # Position text within the leaflet block
    # Ensure text is slightly indented from the border
    text_x_start = x_pos + 0.5 * cm
    text_y_start = y_pos + height - 1.0 * cm # Start from top, move down

    text_obj.setTextOrigin(text_x_start, text_y_start)

    text_obj.textLine("Thank you {name} ji!")
    text_obj.textLine("Thank you for your order — it truly means a lot to us!")
    text_obj.textLine("We hope you love your stole.")
    text_obj.textLine("If you're happy with your purchase")
    text_obj.textLine("we’d be thrilled if you could leave us a ")
    text_obj.textLine("5-star review ⭐⭐⭐⭐⭐")
    text_obj.textLine("In case there’s anything you’re not satisfied with,")
    text_obj.textLine("please reach out to us directly on  ")
    text_obj.textLine("WhatsApp: +91 7860861434")
    text_obj.textLine("Wwe’ll do our best to make it right.")
    text_obj.textLine("Your feedback helps us improve, and your support means")
    text_obj.textLine("the world to our small business.")
    text_obj.textLine("Thank you once again!")
    text_obj.textLine("     ")
    text_obj.textLine("Warm regards,")
    text_obj.textLine("Team Mary Creations")
    text_obj.textLine("")
    text_obj.textLine("")

    c_obj.drawText(text_obj)

# --- Duplicated Name Extraction Logic (from pdf_parser.py, adapted for single page) ---
def _extract_name_from_page_text(page_text: str) -> str:
    """
    Extracts a single customer name from the text of a single Meesho PDF page.
    This is adapted from pdf_parser.py to work with raw page text.
    """
    lines = page_text.split('\n')
    for i, line in enumerate(lines):
        if "CUSTOMER ADDRESS" in line.upper(): # Meesho labels often have this just above name
            if i + 1 < len(lines):
                raw_name = lines[i + 1].strip()
                # Use simplified cleaning (duplicate of clean_customer_name logic)
                if not raw_name or raw_name.isdigit():
                    return ""
                # Remove after comma or hyphen
                raw_name = re.split(r'[,-]', raw_name)[0]
                # Remove digits
                raw_name = re.sub(r'\d+', '', raw_name)
                # Remove extra spaces and take first 2 words
                words = raw_name.strip().split()
                if len(words) >= 2:
                    return " ".join(words[:2])
                elif len(words) == 1:
                    return words[0]
    return ""

# --- Main Hybrid Bill Generation Function ---
def generate_hybrid_bill(input_pdf_path: str, output_pdf_path: str):
    """
    Generates a 'hybrid bill' PDF where each A4 page contains 4 cropped bills
    and 4 corresponding leaflets in the central empty space.
    """
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        raise ValueError(f"Error opening input PDF '{input_pdf_path}': {e}")
    
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    # Dimensions of the content to be cropped from the source PDF (fixed by CROP_RECT)
    crop_original_width = CROP_RECT.width
    crop_original_height = CROP_RECT.height # This is 350 points

    # --- Layout Parameters for Bills and Leaflets ---
    page_outer_margin = 1.0 * cm  # Margin from A4 page edges (all 4 sides)
    inner_gutter = 0.7 * cm       # Space between columns/rows of items

    # Calculate dimensions for bill slots
    # Total width available for 2 bill columns + 1 inner gutter
    available_width_for_2_cols = PAGE_WIDTH - (2 * page_outer_margin) - inner_gutter
    bill_slot_width = available_width_for_2_cols / 2
    
    # Calculate the scale factor for the bills to fit into their slots while maintaining aspect ratio
    scale_factor_for_bill = bill_slot_width / crop_original_width
    bill_display_height = crop_original_height * scale_factor_for_bill # Actual height bills will be drawn at

    # Calculate Y positions for bills to push them towards top/bottom
    # Top row bills will be drawn from: PAGE_HEIGHT - page_outer_margin - bill_display_height (ReportLab Y from bottom)
    # Bottom row bills will be drawn from: page_outer_margin
    y_top_row_bill = PAGE_HEIGHT - page_outer_margin - bill_display_height
    y_bottom_row_bill = page_outer_margin

    # Central leaflet area dimensions
    # The height of the central space between the top and bottom bill rows
    central_leaflet_area_height = y_top_row_bill - (y_bottom_row_bill + bill_display_height + inner_gutter) # Add inner_gutter between bill row and leaflet area
    
    # Calculate dimensions for leaflet slots within the central area (2x2 grid)
    # Leaflet slot width will be same as bill_slot_width (as it occupies the same horizontal space)
    leaflet_slot_width = bill_slot_width
    leaflet_slot_height = (central_leaflet_area_height - inner_gutter) / 2 # Two rows of leaflets + 1 inner gutter

    # --- Bill Slot Positions ---
    # (x_pos, y_pos) for bottom-left of each bill image
    bill_slot_positions = [
        # Top-Left Bill
        (page_outer_margin, y_top_row_bill),
        # Top-Right Bill
        (page_outer_margin + bill_slot_width + inner_gutter, y_top_row_bill),
        # Bottom-Left Bill
        (page_outer_margin, y_bottom_row_bill),
        # Bottom-Right Bill
        (page_outer_margin + bill_slot_width + inner_gutter, y_bottom_row_bill)
    ]

    # --- Leaflet Slot Positions ---
    # (x_pos, y_pos) for bottom-left of each leaflet
    # Leaflets are placed within the central area
    y_leaflet_top_row = y_bottom_row_bill + bill_display_height + inner_gutter + leaflet_slot_height + inner_gutter # Y for top row leaflets
    y_leaflet_bottom_row = y_bottom_row_bill + bill_display_height + inner_gutter # Y for bottom row leaflets

    leaflet_positions = [
        # Top-Left Leaflet in central area
        (page_outer_margin, y_leaflet_top_row),
        # Top-Right Leaflet in central area
        (page_outer_margin + leaflet_slot_width + inner_gutter, y_leaflet_top_row),
        # Bottom-Left Leaflet in central area
        (page_outer_margin, y_leaflet_bottom_row),
        # Bottom-Right Leaflet in central area
        (page_outer_margin + leaflet_slot_width + inner_gutter, y_leaflet_bottom_row)
    ]
    
    current_item_index_on_page = 0 # To track which of the 4 slots we're currently filling on the output page

    # Collect all customer names first to ensure we have them for the leaflets
    all_customer_names = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()
        name = _extract_name_from_page_text(page_text)
        all_customer_names.append(name if name else f"Customer {page_num + 1}") # Fallback name

    # Loop through each page of the input PDF (each page represents one full bill)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # --- Draw Cropped Bill Part ---
        # Render pixmap from the CROP_RECT area at a good resolution (e.g., 200 DPI)
        render_dpi = 200 
        render_scale = render_dpi / 72.0 
        pix = page.get_pixmap(matrix=fitz.Matrix(render_scale, render_scale), clip=CROP_RECT)
        
        # Convert pixmap to an in-memory image suitable for ReportLab
        img_buffer = io.BytesIO(pix.tobytes("png")) 
        img = ImageReader(img_buffer)

        # Get position for the current bill slot
        x_bill_pos, y_bill_pos = bill_slot_positions[current_item_index_on_page]
        
        # Center the bill image within its allocated slot (horizontally and vertically)
        # pix.width and pix.height are already scaled by render_scale
        # We need to calculate the *final* drawing width/height based on bill_display_height/width
        final_bill_draw_width = bill_slot_width
        final_bill_draw_height = bill_display_height

        draw_bill_x = x_bill_pos + (bill_slot_width - final_bill_draw_width) / 2
        draw_bill_y = y_bill_pos + (bill_display_height - final_bill_draw_height) / 2 # Use bill_display_height for vertical centering

        c.drawImage(img, draw_bill_x, draw_bill_y, width=final_bill_draw_width, height=final_bill_draw_height)

        # --- Draw Leaflet Part ---
        customer_name = all_customer_names[page_num] # Get name for current bill
        x_leaflet_pos, y_leaflet_pos = leaflet_positions[current_item_index_on_page]
        
        # Use leaflet_slot_width/height as target dimensions for drawing a single leaflet
        _draw_single_leaflet(c, customer_name, x_leaflet_pos, y_leaflet_pos, leaflet_slot_width, leaflet_slot_height)

        current_item_index_on_page += 1

        # If 4 items (bill+leaflet) have been placed or it's the last bill, show new page
        if current_item_index_on_page == 4 or (page_num == len(doc) - 1 and current_item_index_on_page > 0):
            c.showPage()
            current_item_index_on_page = 0 # Reset slot index for the next output page

    doc.close()
    c.save()

# --- Test block ---
if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("generated", exist_ok=True) 

    test_input_pdf = os.path.join("uploads", "test_multipage_bill.pdf")
    test_output_pdf = os.path.join("generated", "hybrid_bills_test_output.pdf")
    
    # Create a dummy multi-page PDF for testing (e.g., 10 pages)
    temp_doc = fitz.open()
    for i in range(10): # 10 dummy pages, 3 A4 output pages (4+4+2 items)
        page = temp_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        # Simulate content in the "cropped" region (top 350 points)
        page.insert_text((PAGE_WIDTH / 4, 50), f"MEESHO BILL - Order {i+1}", fontsize=20, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, 100), f"Customer: Hybrid User {i+1} Ji!", fontsize=14, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, 150), f"Product: Test Item {i+1}", fontsize=10, color=(0,0,0))
        page.insert_text((PAGE_WIDTH / 4, 200), f"Order No: 123456{i+1}", fontsize=9, color=(0,0,0))
        # Simulate cropped-out content (below 350 points from top)
        page.insert_text((PAGE_WIDTH / 4, 400), f"Financial Details (cropped)", fontsize=10, color=(0.5, 0.5, 0.5))
        page.insert_text((PAGE_WIDTH / 4, 600), f"Other Info (cropped)", fontsize=10, color=(0.5, 0.5, 0.5))
        page.draw_rect(fitz.Rect(20, 20, PAGE_WIDTH - 20, PAGE_HEIGHT - 20), width=0.5)

    temp_doc.save(test_input_pdf)
    temp_doc.close()
    print(f"Created dummy input PDF for testing: {test_input_pdf}")

    try:
        generate_hybrid_bill(test_input_pdf, test_output_pdf)
        print(f"Generated hybrid PDF for testing: {os.path.abspath(test_output_pdf)}")
    except ValueError as e:
        print(f"Test failed: {e}")

    # Optional: Clean up test files
    # os.remove(test_input_pdf)
    # os.remove(test_output_pdf)

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List

# --- Layout Configuration ---
# Page and margin constants
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 1.5 * cm
MARGIN_RIGHT = 1.5 * cm
MARGIN_TOP = 1.5 * cm
MARGIN_BOTTOM = 1.5 * cm
GUTTER = 0.5 * cm # Space between columns

# Grid configuration - CHANGED FOR LONGER MESSAGE
NUM_COLUMNS = 2
NUM_ROWS = 4 # Changed from 9 to 4 to fit the new message
LEAFLETS_PER_PAGE = NUM_COLUMNS * NUM_ROWS

# Calculated dimensions for each leaflet block
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
BLOCK_WIDTH = (USABLE_WIDTH - GUTTER) / NUM_COLUMNS
BLOCK_HEIGHT = USABLE_HEIGHT / NUM_ROWS

def register_fonts():
    """
    Tries to register a font that supports emojis across different operating systems.
    Defaults to Helvetica if no suitable font is found.
    """
    font_name = "EmojiFont"
    font_paths = [
        # Windows paths
        "C:/Windows/Fonts/seguiemj.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        # macOS paths  
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/Library/Fonts/Arial Unicode MS.ttf",
        # Linux paths
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    try:
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
        
        # If no fonts found, use default Helvetica
        return "Helvetica"
    except Exception as e:
        print(f"Font registration warning: Could not load font. {e}")
        return "Helvetica"

def generate_leaflet_pdf(customer_names: List[str], output_pdf_path: str):
    """
    Generates a PDF with personalized leaflets based on the new 2x4 grid layout.
    """
    font = register_fonts()
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    for i, name in enumerate(customer_names):
        # Create a new page if the current one is full
        if i > 0 and i % LEAFLETS_PER_PAGE == 0:
            c.showPage()

        # Calculate position in the grid (2 columns, 4 rows)
        page_index = i % LEAFLETS_PER_PAGE
        col = page_index % NUM_COLUMNS
        row = page_index // NUM_COLUMNS

        # Calculate the x, y coordinates for the bottom-left corner of the block
        x = MARGIN_LEFT + col * (BLOCK_WIDTH + GUTTER)
        y = PAGE_HEIGHT - MARGIN_TOP - (row + 1) * BLOCK_HEIGHT

        # Draw a dashed border for cutting guide
        c.setDash(1, 2)
        c.rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
        c.setDash([], 0)

        # --- NEW LEAFLET MESSAGE ---
        text = c.beginText()
        text.setFont(font, 8) # Slightly smaller font to ensure fit
        text.setLeading(10)  # Line spacing
        # Set text origin with a margin inside the leaflet block
        text.setTextOrigin(x + 0.5 * cm, y + BLOCK_HEIGHT - 0.8 * cm)

        text.textLine(f"Thank you {name} ji!")
        text.textLine("Thank you for your order — it truly means a lot to us!")
        text.textLine("We hope you love your stole.")
   
        text.textLine("If you're happy with your purchase,")
        text.textLine("we’d be thrilled if you could leave us a")
        text.textLine("5-star review ⭐⭐⭐⭐⭐")
        
        text.textLine("In case there’s anything you’re not satisfied with,")
        text.textLine("please reach out to us directly on")
        text.textLine("WhatsApp: +91 7860861434")
        text.textLine("we’ll do our best to make it right.")
        
        text.textLine("Your feedback helps us improve, and your support means")
        text.textLine("the world to our small business.")
        text.textLine(" ") # Blank line for spacing
        text.textLine("Thank you once again!")
        text.textLine(" ") # Blank line for spacing
        text.textLine("Warm regards,")
        text.textLine("Team Mary Creations.")

        c.drawText(text)

    # Save the PDF document
    c.save()
    print(f"✅ Leaflet generated successfully at: {output_pdf_path}")

# --- Test Mode ---
# This block runs only when you execute the script directly (e.g., `python leaflet_maker.py`)
if __name__ == '__main__':
    # Create a list of dummy names to test the PDF generation
    # Let's test with 10 names to see how it handles multiple pages
    test_names = [f"Customer {i}" for i in range(1, 11)]

    # Create a directory to save the test file
    output_directory = "generated_leaflets"
    os.makedirs(output_directory, exist_ok=True)
    
    # Define the output file path
    output_file = os.path.join(output_directory, "leaflet_2x4_layout_test.pdf")
    
    # Generate the PDF
    generate_leaflet_pdf(test_names, output_file)
    
    print(f"📄 Test PDF saved at: {os.path.abspath(output_file)}")

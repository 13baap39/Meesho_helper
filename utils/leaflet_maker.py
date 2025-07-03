import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List

# Layout constants
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 1.5 * cm
MARGIN_RIGHT = 1.5 * cm
MARGIN_TOP = 1.5 * cm
MARGIN_BOTTOM = 1.5 * cm
GUTTER = 0.5 * cm

NUM_COLUMNS = 2
NUM_ROWS = 9
LEAFLETS_PER_PAGE = NUM_COLUMNS * NUM_ROWS

USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

BLOCK_WIDTH = (USABLE_WIDTH - GUTTER) / NUM_COLUMNS
BLOCK_HEIGHT = USABLE_HEIGHT / NUM_ROWS

# Register emoji-capable font
def register_fonts():
    emoji_font = "Helvetica"
    try:
        emoji_path = "C:/Windows/Fonts/seguiemj.ttf"
        if os.path.exists(emoji_path):
            pdfmetrics.registerFont(TTFont("EmojiFont", emoji_path))
            emoji_font = "EmojiFont"
    except Exception as e:
        print("Font registration error:", e)
    return emoji_font

# Generate the leaflet PDF
def generate_leaflet_pdf(customer_names: List[str], output_pdf_path: str):
    font = register_fonts()
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    for i, name in enumerate(customer_names):
        # NEW PAGE IF NEEDED
        if i > 0 and i % LEAFLETS_PER_PAGE == 0:
            c.showPage()

        page_index = i % LEAFLETS_PER_PAGE
        col = page_index % NUM_COLUMNS
        row = page_index // NUM_COLUMNS

        x = MARGIN_LEFT + col * (BLOCK_WIDTH + GUTTER)
        y = PAGE_HEIGHT - MARGIN_TOP - (row + 1) * BLOCK_HEIGHT

        # Draw border
        c.setDash(1, 2)
        c.rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
        c.setDash([], 0)

        # Draw text
        text = c.beginText()
        text.setFont(font, 9)
        text.setLeading(10.2)
        text.setTextOrigin(x + 0.5 * cm, y + BLOCK_HEIGHT - 1.0 * cm)

        text.textLine(f"🙏 Thank you {name} ji!")
        text.textLine("Aapka order humare liye khaas hai 💛")
        text.textLine("Agar pasand aaye toh please")
        text.textLine("5-star rating dein ⭐⭐⭐⭐⭐")
        text.textLine("Agar stole pasand na aaya ho toh")
        text.textLine("WhatsApp karein 📱 7860861434")

        c.drawText(text)

    # Forcefully end with blank draw so last page is preserved
    c.showPage()
    c.save()
    print(f"✅ Leaflet generated at: {output_pdf_path}")

# Test mode
if __name__ == '__main__':
    names = [f"Customer {i}" for i in range(1, 29)]  # 28 names
    out_dir = "generated_leaflets"
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "leaflet_multi_page_fixed.pdf")
    generate_leaflet_pdf(names, output_path)
    print("📄 PDF saved at:", os.path.abspath(output_path))
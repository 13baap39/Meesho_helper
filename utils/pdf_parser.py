import fitz  # PyMuPDF
from typing import List
import os
import re

def extract_customer_names(pdf_path: str) -> List[str]:
    """
    Extracts only customer names from a Meesho PDF label.
    Looks for lines after "BILL TO / SHIP TO" and cleans names by removing address parts.
    """
    unique_names = set()

    try:
        document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    for page in document:
        text = page.get_text()
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if "BILL TO / SHIP TO" in line.upper():
                if i + 1 < len(lines):
                    raw_name = lines[i + 1].strip()
                    cleaned = clean_customer_name(raw_name)
                    if cleaned:
                        unique_names.add(cleaned)

    document.close()
    return sorted(unique_names)

def clean_customer_name(text: str) -> str:
    """
    Cleans the extracted line to return only the name.
    Removes addresses, commas, hyphens, numbers etc.
    """
    if not text or text.isdigit():
        return ""

    # Remove after comma or hyphen
    text = re.split(r'[,-]', text)[0]

    # Remove digits
    text = re.sub(r'\d+', '', text)

    # Remove extra spaces
    words = text.strip().split()

    # Return first 2 words only (like "Rafey Khan", "Mariam Fatima")
    if len(words) >= 2:
        return " ".join(words[:2])
    elif len(words) == 1:
        return words[0]
    return ""

# --- Test block ---
if __name__ == '__main__':
    sample_pdf = os.path.join("uploads", "sample_orders.pdf")
    os.makedirs("uploads", exist_ok=True)

    try:
        # Create test PDF
        doc = fitz.open()
        page = doc.new_page()
        sample_text = """
        BILL TO / SHIP TO
        Afrakhatun - Shyamnagar, Lowhat Hatoya Road

        BILL TO / SHIP TO
        Mohit Singh - Sonu Medikal, SH 35, Kareeriya

        BILL TO / SHIP TO
        Maryam Fatima - Bhiwandi, Maharashtra
        """
        page.insert_text((72, 72), sample_text, fontsize=11)
        doc.save(sample_pdf)
        doc.close()

        print("✅ Sample PDF created.")

        names = extract_customer_names(sample_pdf)
        print("\n📦 Extracted Names:")
        for name in names:
            print(f"– {name}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
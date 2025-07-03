# 📄 Meesho PDF Utility

Welcome to the **Meesho PDF Utility**! This is a powerful, user-friendly web application designed to help Meesho sellers efficiently manage and process their order labels and bills. It streamlines several common tasks, making your shipping and customer communication processes faster and more personalized.

## ✨ What Does It Do?

This utility provides a seamless experience for transforming your raw Meesho order documents into actionable, print-ready files, accessible through a clean web interface.

### Key Features:

1.  **Leaflet Generator:**
    * **Purpose:** Add a personal touch to every order.
    * **How it Works:** Simply upload your Meesho Order Label PDF, and the app will automatically extract customer names. It then generates a print-ready PDF containing personalized "Thank You" leaflets for each customer, perfect for including in your packages.

2.  **Bill Cropper:**
    * **Purpose:** Efficiently prepare shipping labels from bulk orders.
    * **How it Works:** Upload your full multi-page Meesho Bill PDF. The utility intelligently crops each individual bill (removing unnecessary financial details and redundant address blocks) and then arranges 4 perfectly sized shipping labels onto a single A4 page, optimized for printing.

3.  **Hybrid Bill Generator:**
    * **Purpose:** A comprehensive, all-in-one printout for streamlined order processing.
    * **How it Works:** Upload your full multi-page Meesho Bill PDF. This advanced feature generates a unique A4 PDF page that combines both the cropped shipping labels and personalized thank-you messages. Each A4 page contains:
        * 4 precisely cropped shipping labels (arranged at the corners of the page).
        * 4 corresponding personalized "Thank You" leaflets, neatly placed in the large central space between the labels. This ensures you have both the label and a personalized note on one convenient sheet.

## 🚀 How It Works (Behind the Scenes)

This application is built using a robust set of technologies to ensure accurate and efficient PDF processing:

* **Flask:** Powers the web application, handling file uploads and serving the user interface.
* **PyMuPDF (fitz):** Used for its high performance in reading, parsing, and extracting specific content from your PDF documents.
* **ReportLab:** Employed for dynamically generating new PDF documents, laying out the cropped bills and personalized leaflets with precision.
* **Pillow (PIL Fork):** Assists with in-memory image manipulation during the PDF processing stages.
* **Web Technologies:** Standard HTML, CSS, and JavaScript provide the interactive and user-friendly interface you interact with.

## 💡 Future Possibilities

We are always looking for ways to enhance this utility. Future ideas include:

* **Batch Processing:** Processing multiple bill PDFs simultaneously.
* **Enhanced Customization:** More options for personalizing leaflet messages, fonts, or fine-tuning cropping areas.
* **User Management:** Features like user accounts and dashboards to manage past uploads and generated files.

---

*Feel free to explore and utilize this tool for your Meesho selling needs!*

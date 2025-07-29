package com.meeshohelper.utils;

import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfPage;
import com.itextpdf.kernel.pdf.PdfReader;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.kernel.pdf.canvas.parser.PdfTextExtractor;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.geom.Rectangle;
import com.itextpdf.kernel.pdf.xobject.PdfFormXObject;
import com.itextpdf.kernel.pdf.canvas.PdfCanvas;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Text;
import com.itextpdf.layout.property.TextAlignment;
import com.itextpdf.kernel.font.PdfFont;
import com.itextpdf.kernel.font.PdfFontFactory;
import com.itextpdf.io.font.constants.StandardFonts;

import com.meeshohelper.models.CustomerData;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PDFProcessor {

    /**
     * Extract customer names from Meesho PDF
     */
    public static List<CustomerData> extractCustomerNames(File pdfFile) throws IOException {
        Set<String> uniqueNames = new HashSet<>();
        List<CustomerData> customers = new ArrayList<>();

        try (PdfReader reader = new PdfReader(pdfFile.getAbsolutePath());
             PdfDocument pdfDoc = new PdfDocument(reader)) {

            int numPages = pdfDoc.getNumberOfPages();
            for (int i = 1; i <= numPages; i++) {
                PdfPage page = pdfDoc.getPage(i);
                String text = PdfTextExtractor.getTextFromPage(page);
                String[] lines = text.split("\n");

                for (int j = 0; j < lines.length; j++) {
                    String line = lines[j].trim();
                    if (line.toUpperCase().contains("BILL TO") || 
                        line.toUpperCase().contains("SHIP TO") ||
                        line.toUpperCase().contains("BILL TO / SHIP TO")) {
                        
                        // Look for the name in the next line
                        if (j + 1 < lines.length) {
                            String rawName = lines[j + 1].trim();
                            String cleanedName = cleanCustomerName(rawName);
                            if (cleanedName != null && !cleanedName.isEmpty() && 
                                !uniqueNames.contains(cleanedName)) {
                                uniqueNames.add(cleanedName);
                                customers.add(new CustomerData(cleanedName));
                            }
                        }
                    }
                }
            }
        }

        return customers;
    }

    /**
     * Clean customer name by removing address parts and unwanted text
     */
    private static String cleanCustomerName(String rawName) {
        if (rawName == null || rawName.trim().isEmpty()) {
            return null;
        }

        // Remove common address keywords and patterns
        String cleaned = rawName
                .replaceAll("(?i)\\b(house|h\\.no|h\\.no\\.|flat|apartment|apt|road|rd|street|st|lane|ln|area|sector|block|plot|pin|pincode|pin code|zip|postal|post|near|opp|opposite|behind|beside|next to|above|below)\\b.*", "")
                .replaceAll("(?i)\\b(city|district|state|country|india|pin|pincode|\\d{6})\\b.*", "")
                .replaceAll("\\d{6,}", "") // Remove pincode-like numbers
                .replaceAll("[,;].*", "") // Remove everything after comma or semicolon
                .replaceAll("\\s+", " ") // Replace multiple spaces with single space
                .trim();

        // Remove if it's just numbers or too short
        if (cleaned.matches("\\d+") || cleaned.length() < 2) {
            return null;
        }

        // Capitalize first letter of each word
        String[] words = cleaned.split("\\s+");
        StringBuilder result = new StringBuilder();
        for (String word : words) {
            if (word.length() > 0) {
                result.append(Character.toUpperCase(word.charAt(0)))
                      .append(word.substring(1).toLowerCase())
                      .append(" ");
            }
        }

        return result.toString().trim();
    }

    /**
     * Crop a specific area from a PDF page
     */
    public static Rectangle cropBillArea(PdfPage page) {
        Rectangle pageRect = page.getPageSize();
        float pageWidth = pageRect.getWidth();
        float pageHeight = pageRect.getHeight();

        // Meesho bill cropping parameters (adjust as needed)
        // These values are approximations and may need fine-tuning
        float cropX = pageWidth * 0.05f; // 5% from left
        float cropY = pageHeight * 0.3f; // 30% from bottom
        float cropWidth = pageWidth * 0.9f; // 90% of page width
        float cropHeight = pageHeight * 0.4f; // 40% of page height

        return new Rectangle(cropX, cropY, cropWidth, cropHeight);
    }

    /**
     * Create a 4-up layout of cropped bills
     */
    public static void createFourUpLayout(File inputFile, File outputFile) throws IOException {
        try (PdfReader reader = new PdfReader(inputFile.getAbsolutePath());
             PdfDocument inputDoc = new PdfDocument(reader);
             PdfWriter writer = new PdfWriter(outputFile.getAbsolutePath());
             PdfDocument outputDoc = new PdfDocument(writer)) {

            PageSize a4 = PageSize.A4;
            float pageWidth = a4.getWidth();
            float pageHeight = a4.getHeight();
            
            // Calculate dimensions for 4-up layout (2x2 grid)
            float billWidth = pageWidth / 2 - 20; // Margin of 10 points on each side
            float billHeight = pageHeight / 2 - 20;

            int inputPages = inputDoc.getNumberOfPages();
            int billsProcessed = 0;
            PdfPage currentOutputPage = null;
            PdfCanvas canvas = null;

            for (int i = 1; i <= inputPages; i++) {
                PdfPage inputPage = inputDoc.getPage(i);
                Rectangle cropArea = cropBillArea(inputPage);
                
                // Create form XObject from cropped area
                PdfFormXObject form = new PdfFormXObject(cropArea);
                PdfCanvas formCanvas = new PdfCanvas(form, outputDoc);
                formCanvas.addXObjectAt(inputPage.copyAsFormXObject(outputDoc), -cropArea.getX(), -cropArea.getY());

                // Create new output page every 4 bills
                if (billsProcessed % 4 == 0) {
                    currentOutputPage = outputDoc.addNewPage(a4);
                    canvas = new PdfCanvas(currentOutputPage);
                }

                // Calculate position for current bill (2x2 grid)
                int position = billsProcessed % 4;
                float x = (position % 2) * (billWidth + 20) + 10;
                float y = pageHeight - ((position / 2) + 1) * (billHeight + 20) + 10;

                // Scale form to fit in allocated space
                float scaleX = billWidth / cropArea.getWidth();
                float scaleY = billHeight / cropArea.getHeight();
                float scale = Math.min(scaleX, scaleY);

                canvas.saveState();
                canvas.concatMatrix(scale, 0, 0, scale, x, y);
                canvas.addXObjectAt(form, 0, 0);
                canvas.restoreState();

                billsProcessed++;
            }
        }
    }

    /**
     * Generate hybrid bill (cropped bills + leaflets)
     */
    public static void generateHybridBill(File inputFile, File outputFile, List<CustomerData> customers) throws IOException {
        try (PdfReader reader = new PdfReader(inputFile.getAbsolutePath());
             PdfDocument inputDoc = new PdfDocument(reader);
             PdfWriter writer = new PdfWriter(outputFile.getAbsolutePath());
             PdfDocument outputDoc = new PdfDocument(writer)) {

            PageSize a4 = PageSize.A4;
            float pageWidth = a4.getWidth();
            float pageHeight = a4.getHeight();
            
            // Layout: 4 bills at corners, leaflets in center
            float billWidth = pageWidth * 0.4f;
            float billHeight = pageHeight * 0.25f;
            float centerWidth = pageWidth * 0.6f;
            float centerHeight = pageHeight * 0.5f;

            int inputPages = inputDoc.getNumberOfPages();
            int billsProcessed = 0;
            int customerIndex = 0;

            for (int i = 1; i <= inputPages; i += 4) {
                PdfPage outputPage = outputDoc.addNewPage(a4);
                PdfCanvas canvas = new PdfCanvas(outputPage);

                // Add 4 bills at corners
                for (int j = 0; j < 4 && (i + j) <= inputPages; j++) {
                    PdfPage inputPage = inputDoc.getPage(i + j);
                    Rectangle cropArea = cropBillArea(inputPage);
                    
                    PdfFormXObject form = new PdfFormXObject(cropArea);
                    PdfCanvas formCanvas = new PdfCanvas(form, outputDoc);
                    formCanvas.addXObjectAt(inputPage.copyAsFormXObject(outputDoc), -cropArea.getX(), -cropArea.getY());

                    // Position at corners
                    float x, y;
                    switch (j) {
                        case 0: x = 10; y = pageHeight - billHeight - 10; break; // Top-left
                        case 1: x = pageWidth - billWidth - 10; y = pageHeight - billHeight - 10; break; // Top-right
                        case 2: x = 10; y = 10; break; // Bottom-left
                        case 3: x = pageWidth - billWidth - 10; y = 10; break; // Bottom-right
                        default: continue;
                    }

                    float scale = Math.min(billWidth / cropArea.getWidth(), billHeight / cropArea.getHeight());
                    canvas.saveState();
                    canvas.concatMatrix(scale, 0, 0, scale, x, y);
                    canvas.addXObjectAt(form, 0, 0);
                    canvas.restoreState();
                }

                // Add leaflets in center
                addLeafletsToCenter(outputDoc, outputPage, customers, customerIndex, centerWidth, centerHeight, pageWidth, pageHeight);
                customerIndex += 4;
            }
        }
    }

    /**
     * Add leaflets to the center of the page
     */
    private static void addLeafletsToCenter(PdfDocument doc, PdfPage page, List<CustomerData> customers, 
                                          int startIndex, float centerWidth, float centerHeight, 
                                          float pageWidth, float pageHeight) {
        try (Document document = new Document(doc)) {
            PdfFont font = PdfFontFactory.createFont(StandardFonts.HELVETICA);
            
            float centerX = (pageWidth - centerWidth) / 2;
            float centerY = (pageHeight - centerHeight) / 2;
            
            for (int i = 0; i < 4 && (startIndex + i) < customers.size(); i++) {
                CustomerData customer = customers.get(startIndex + i);
                
                float leafletWidth = centerWidth / 2 - 10;
                float leafletHeight = centerHeight / 2 - 10;
                float x = centerX + (i % 2) * (leafletWidth + 10);
                float y = centerY + (i / 2) * (leafletHeight + 10);
                
                // Create thank you message
                String thankYouMessage = createThankYouMessage(customer.getName());
                
                Paragraph paragraph = new Paragraph()
                    .setFont(font)
                    .setFontSize(10)
                    .setTextAlignment(TextAlignment.CENTER)
                    .add(new Text(thankYouMessage));
                
                // Position the paragraph (this is simplified - in real implementation,
                // you'd need to properly position and size the text within the rectangle)
                document.showTextAligned(paragraph, x + leafletWidth/2, y + leafletHeight/2, 
                                       TextAlignment.CENTER);
            }
        } catch (IOException e) {
            // Handle font creation error
            e.printStackTrace();
        }
    }

    /**
     * Create thank you message for customer
     */
    private static String createThankYouMessage(String customerName) {
        return String.format("Dear %s,\n\n" +
                "Thank you for choosing us!\n" +
                "Your order has been dispatched.\n\n" +
                "For queries, contact us on\n" +
                "WhatsApp: +91 7860861434\n\n" +
                "Please rate us 5 stars!\n\n" +
                "With love,\n" +
                "Your Seller", customerName);
    }
}
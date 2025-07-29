package com.meeshohelper.utils;

import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfPage;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.borders.Border;
import com.itextpdf.layout.element.Cell;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.property.TextAlignment;
import com.itextpdf.layout.property.UnitValue;
import com.itextpdf.kernel.font.PdfFont;
import com.itextpdf.kernel.font.PdfFontFactory;
import com.itextpdf.io.font.constants.StandardFonts;
import com.itextpdf.kernel.colors.ColorConstants;

import com.meeshohelper.models.CustomerData;

import java.io.File;
import java.io.IOException;
import java.util.List;

public class LeafletGenerator {

    private static final int LEAFLETS_PER_PAGE = 8; // 2 columns x 4 rows
    private static final float MARGIN = 20f;
    private static final String WHATSAPP_NUMBER = "+91 7860861434";

    /**
     * Generate leaflet PDF with thank you messages for customers
     */
    public static void generateLeafletPDF(List<CustomerData> customers, File outputFile) throws IOException {
        try (PdfWriter writer = new PdfWriter(outputFile.getAbsolutePath());
             PdfDocument pdfDoc = new PdfDocument(writer);
             Document document = new Document(pdfDoc, PageSize.A4)) {

            document.setMargins(MARGIN, MARGIN, MARGIN, MARGIN);

            PdfFont boldFont = PdfFontFactory.createFont(StandardFonts.HELVETICA_BOLD);
            PdfFont regularFont = PdfFontFactory.createFont(StandardFonts.HELVETICA);

            int customersProcessed = 0;
            int totalCustomers = customers.size();

            while (customersProcessed < totalCustomers) {
                // Create table for leaflets layout (2 columns)
                Table table = new Table(2);
                table.setWidth(UnitValue.createPercentValue(100));

                // Add leaflets to current page
                for (int i = 0; i < LEAFLETS_PER_PAGE && customersProcessed < totalCustomers; i++) {
                    CustomerData customer = customers.get(customersProcessed);
                    Cell leafletCell = createLeafletCell(customer, boldFont, regularFont);
                    table.addCell(leafletCell);
                    customersProcessed++;
                }

                // Fill remaining cells if needed to maintain layout
                int cellsToFill = LEAFLETS_PER_PAGE - (customersProcessed % LEAFLETS_PER_PAGE);
                if (cellsToFill > 0 && cellsToFill < LEAFLETS_PER_PAGE) {
                    for (int i = 0; i < cellsToFill; i++) {
                        Cell emptyCell = new Cell()
                                .setBorder(Border.NO_BORDER)
                                .setHeight(80); // Same height as leaflet cells
                        table.addCell(emptyCell);
                    }
                }

                document.add(table);

                // Add new page if there are more customers
                if (customersProcessed < totalCustomers) {
                    document.add(new com.itextpdf.layout.element.AreaBreak());
                }
            }
        }
    }

    /**
     * Create a single leaflet cell with thank you message
     */
    private static Cell createLeafletCell(CustomerData customer, PdfFont boldFont, PdfFont regularFont) {
        Cell cell = new Cell()
                .setPadding(8)
                .setBorder(com.itextpdf.layout.borders.SolidBorder.createSolidBorder(ColorConstants.BLACK, 1))
                .setHeight(100)
                .setBackgroundColor(ColorConstants.WHITE);

        // Customer name (greeting)
        Paragraph greeting = new Paragraph("Dear " + customer.getName() + ",")
                .setFont(boldFont)
                .setFontSize(10)
                .setTextAlignment(TextAlignment.LEFT)
                .setMarginBottom(5);

        // Thank you message
        Paragraph thankYou = new Paragraph("Thank you for choosing us!")
                .setFont(boldFont)
                .setFontSize(9)
                .setTextAlignment(TextAlignment.CENTER)
                .setMarginBottom(3);

        // Order dispatched message
        Paragraph orderInfo = new Paragraph("Your order has been dispatched.")
                .setFont(regularFont)
                .setFontSize(8)
                .setTextAlignment(TextAlignment.CENTER)
                .setMarginBottom(5);

        // Contact information
        Paragraph contact = new Paragraph("For any queries, contact us on")
                .setFont(regularFont)
                .setFontSize(7)
                .setTextAlignment(TextAlignment.CENTER)
                .setMarginBottom(2);

        Paragraph whatsapp = new Paragraph("WhatsApp: " + WHATSAPP_NUMBER)
                .setFont(boldFont)
                .setFontSize(8)
                .setTextAlignment(TextAlignment.CENTER)
                .setMarginBottom(5);

        // Rating request
        Paragraph rating = new Paragraph("Please rate us ⭐⭐⭐⭐⭐ on the app!")
                .setFont(regularFont)
                .setFontSize(7)
                .setTextAlignment(TextAlignment.CENTER)
                .setMarginBottom(5);

        // Closing
        Paragraph closing = new Paragraph("With love,\nYour Seller")
                .setFont(regularFont)
                .setFontSize(7)
                .setTextAlignment(TextAlignment.RIGHT)
                .setMarginBottom(0);

        // Add all paragraphs to cell
        cell.add(greeting);
        cell.add(thankYou);
        cell.add(orderInfo);
        cell.add(contact);
        cell.add(whatsapp);
        cell.add(rating);
        cell.add(closing);

        return cell;
    }

    /**
     * Generate a simple leaflet PDF with basic layout
     */
    public static void generateSimpleLeafletPDF(List<CustomerData> customers, File outputFile) throws IOException {
        try (PdfWriter writer = new PdfWriter(outputFile.getAbsolutePath());
             PdfDocument pdfDoc = new PdfDocument(writer);
             Document document = new Document(pdfDoc, PageSize.A4)) {

            document.setMargins(30, 30, 30, 30);

            PdfFont boldFont = PdfFontFactory.createFont(StandardFonts.HELVETICA_BOLD);
            PdfFont regularFont = PdfFontFactory.createFont(StandardFonts.HELVETICA);

            // Title
            Paragraph title = new Paragraph("Thank You Leaflets")
                    .setFont(boldFont)
                    .setFontSize(16)
                    .setTextAlignment(TextAlignment.CENTER)
                    .setMarginBottom(20);
            document.add(title);

            // Create leaflets for each customer
            for (int i = 0; i < customers.size(); i++) {
                CustomerData customer = customers.get(i);

                // Add separator line before each leaflet (except the first)
                if (i > 0) {
                    document.add(new Paragraph("─".repeat(60))
                            .setTextAlignment(TextAlignment.CENTER)
                            .setMarginTop(10)
                            .setMarginBottom(10));
                }

                // Customer leaflet content
                addLeafletContent(document, customer, boldFont, regularFont);

                // Add some space after each leaflet
                document.add(new Paragraph("\n"));
            }
        }
    }

    /**
     * Add leaflet content for a single customer
     */
    private static void addLeafletContent(Document document, CustomerData customer, 
                                        PdfFont boldFont, PdfFont regularFont) {
        // Greeting
        Paragraph greeting = new Paragraph("Dear " + customer.getName() + ",")
                .setFont(boldFont)
                .setFontSize(12)
                .setTextAlignment(TextAlignment.LEFT)
                .setMarginBottom(8);
        document.add(greeting);

        // Thank you message
        Paragraph thankYou = new Paragraph("Thank you for choosing us! Your order has been dispatched.")
                .setFont(regularFont)
                .setFontSize(10)
                .setTextAlignment(TextAlignment.LEFT)
                .setMarginBottom(10);
        document.add(thankYou);

        // Contact info
        Paragraph contact = new Paragraph("For any queries, contact us on WhatsApp: " + WHATSAPP_NUMBER)
                .setFont(regularFont)
                .setFontSize(10)
                .setTextAlignment(TextAlignment.LEFT)
                .setMarginBottom(8);
        document.add(contact);

        // Rating request
        Paragraph rating = new Paragraph("Please rate us 5 stars ⭐⭐⭐⭐⭐ on the app!")
                .setFont(regularFont)
                .setFontSize(10)
                .setTextAlignment(TextAlignment.LEFT)
                .setMarginBottom(10);
        document.add(rating);

        // Closing
        Paragraph closing = new Paragraph("With love,\nYour Seller")
                .setFont(regularFont)
                .setFontSize(10)
                .setTextAlignment(TextAlignment.RIGHT)
                .setMarginBottom(5);
        document.add(closing);
    }

    /**
     * Create a formatted thank you message string
     */
    public static String createThankYouMessage(String customerName) {
        return String.format(
                "Dear %s,\n\n" +
                "Thank you for choosing us!\n" +
                "Your order has been dispatched.\n\n" +
                "For any queries, contact us on\n" +
                "WhatsApp: %s\n\n" +
                "Please rate us 5 stars ⭐⭐⭐⭐⭐ on the app!\n\n" +
                "With love,\n" +
                "Your Seller",
                customerName, WHATSAPP_NUMBER
        );
    }

    /**
     * Validate customer data before generating leaflets
     */
    public static boolean validateCustomerData(List<CustomerData> customers) {
        if (customers == null || customers.isEmpty()) {
            return false;
        }

        for (CustomerData customer : customers) {
            if (customer.getName() == null || customer.getName().trim().isEmpty()) {
                return false;
            }
        }

        return true;
    }
}
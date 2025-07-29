package com.meeshohelper.activities;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.content.FileProvider;

import com.meeshohelper.R;
import com.meeshohelper.models.CustomerData;
import com.meeshohelper.utils.FileManager;
import com.meeshohelper.utils.PDFProcessor;

import java.io.File;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class HybridBillActivity extends AppCompatActivity {

    private Button btnSelectFile, btnProcess, btnDownload, btnShare;
    private TextView tvSelectedFile, tvFileSize, tvProcessingStatus, tvProcessingDetails, 
                    tvCustomerProgress, tvResultInfo, tvCustomerInfo;
    private CardView cardProcessing;
    private LinearLayout layoutResults;
    private ProgressBar progressBar;

    private FileManager fileManager;
    private ExecutorService executorService;
    private ActivityResultLauncher<String[]> filePickerLauncher;

    private File selectedFile;
    private File outputFile;
    private List<CustomerData> extractedCustomers;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_hybrid_bill);

        // Initialize components
        initializeViews();
        setupToolbar();
        initializeServices();
        setupFilePickerLauncher();
        setupClickListeners();
    }

    private void initializeViews() {
        btnSelectFile = findViewById(R.id.btnSelectFile);
        btnProcess = findViewById(R.id.btnProcess);
        btnDownload = findViewById(R.id.btnDownload);
        btnShare = findViewById(R.id.btnShare);
        
        tvSelectedFile = findViewById(R.id.tvSelectedFile);
        tvFileSize = findViewById(R.id.tvFileSize);
        tvProcessingStatus = findViewById(R.id.tvProcessingStatus);
        tvProcessingDetails = findViewById(R.id.tvProcessingDetails);
        tvCustomerProgress = findViewById(R.id.tvCustomerProgress);
        tvResultInfo = findViewById(R.id.tvResultInfo);
        tvCustomerInfo = findViewById(R.id.tvCustomerInfo);
        
        cardProcessing = findViewById(R.id.cardProcessing);
        layoutResults = findViewById(R.id.layoutResults);
        progressBar = findViewById(R.id.progressBar);
    }

    private void setupToolbar() {
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle(R.string.hybrid_bill_generator);
        }
    }

    private void initializeServices() {
        fileManager = new FileManager(this);
        executorService = Executors.newSingleThreadExecutor();
    }

    private void setupFilePickerLauncher() {
        filePickerLauncher = registerForActivityResult(
                new ActivityResultContracts.OpenDocument(),
                uri -> {
                    if (uri != null) {
                        handleSelectedFile(uri);
                    }
                }
        );
    }

    private void setupClickListeners() {
        btnSelectFile.setOnClickListener(v -> openFilePicker());
        btnProcess.setOnClickListener(v -> processSelectedFile());
        btnDownload.setOnClickListener(v -> downloadFile());
        btnShare.setOnClickListener(v -> shareFile());
    }

    private void openFilePicker() {
        String[] mimeTypes = {"application/pdf"};
        filePickerLauncher.launch(mimeTypes);
    }

    private void handleSelectedFile(Uri uri) {
        try {
            // Get file name from URI
            String fileName = "selected_hybrid_bill.pdf";
            
            // Copy file to app's internal storage
            selectedFile = fileManager.copyFileFromUri(uri, fileName);
            
            // Get file size
            String fileSize = FileManager.getReadableFileSize(selectedFile.length());
            
            // Update UI
            tvSelectedFile.setText(getString(R.string.file_selected, fileName));
            tvFileSize.setText("File size: " + fileSize);
            tvFileSize.setVisibility(View.VISIBLE);
            btnProcess.setEnabled(true);
            
        } catch (Exception e) {
            Toast.makeText(this, getString(R.string.error_processing, e.getMessage()), 
                          Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }
    }

    private void processSelectedFile() {
        if (selectedFile == null) {
            Toast.makeText(this, R.string.no_file_selected, Toast.LENGTH_SHORT).show();
            return;
        }

        // Show processing UI
        showProcessingState(true);
        btnProcess.setEnabled(false);

        // Process file in background
        executorService.execute(() -> {
            try {
                runOnUiThread(() -> {
                    tvProcessingStatus.setText("Analyzing PDF content...");
                    tvProcessingDetails.setText("Reading bill structure and extracting data");
                    tvCustomerProgress.setText("");
                });

                // Extract customer names first
                runOnUiThread(() -> {
                    tvProcessingStatus.setText("Extracting customer names...");
                    tvProcessingDetails.setText("Finding customer information from order labels");
                });

                extractedCustomers = PDFProcessor.extractCustomerNames(selectedFile);
                
                if (extractedCustomers.isEmpty()) {
                    runOnUiThread(() -> {
                        showProcessingState(false);
                        btnProcess.setEnabled(true);
                        Toast.makeText(HybridBillActivity.this, 
                                     R.string.error_no_customers, Toast.LENGTH_LONG).show();
                    });
                    return;
                }

                runOnUiThread(() -> {
                    tvCustomerProgress.setText("Found " + extractedCustomers.size() + " customers");
                });

                // Generate output filename
                String outputFileName = fileManager.generateOutputFilename(
                        selectedFile.getName(), "hybrid_bills");
                outputFile = new File(fileManager.getOutputDirectory(), outputFileName);

                runOnUiThread(() -> {
                    tvProcessingStatus.setText("Creating hybrid bills...");
                    tvProcessingDetails.setText("Combining cropped bills with personalized leaflets");
                });

                // Generate hybrid bill PDF
                PDFProcessor.generateHybridBill(selectedFile, outputFile, extractedCustomers);

                runOnUiThread(() -> {
                    showProcessingState(false);
                    showResults();
                    btnProcess.setEnabled(true);
                });

            } catch (Exception e) {
                runOnUiThread(() -> {
                    showProcessingState(false);
                    btnProcess.setEnabled(true);
                    Toast.makeText(HybridBillActivity.this, 
                                 getString(R.string.error_processing, e.getMessage()), 
                                 Toast.LENGTH_LONG).show();
                });
                e.printStackTrace();
            }
        });
    }

    private void showProcessingState(boolean isProcessing) {
        cardProcessing.setVisibility(isProcessing ? View.VISIBLE : View.GONE);
        layoutResults.setVisibility(View.GONE);
    }

    private void showResults() {
        layoutResults.setVisibility(View.VISIBLE);
        
        String resultText = "Successfully created hybrid bills with cropped order labels and personalized thank-you leaflets.";
        if (outputFile != null && outputFile.exists()) {
            String outputSize = FileManager.getReadableFileSize(outputFile.length());
            resultText += "\nOutput file size: " + outputSize;
        }
        
        tvResultInfo.setText(resultText);
        
        // Show customer information
        String customerInfoText = "Customer leaflets generated for:\n";
        int maxShow = Math.min(extractedCustomers.size(), 5); // Show max 5 names
        for (int i = 0; i < maxShow; i++) {
            customerInfoText += "• " + extractedCustomers.get(i).getName() + "\n";
        }
        if (extractedCustomers.size() > 5) {
            customerInfoText += "... and " + (extractedCustomers.size() - 5) + " more customers";
        }
        
        tvCustomerInfo.setText(customerInfoText);
        
        Toast.makeText(this, R.string.processing_complete, Toast.LENGTH_SHORT).show();
    }

    private void downloadFile() {
        if (outputFile == null || !outputFile.exists()) {
            Toast.makeText(this, "No file to download", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            // Create intent to open the file
            Uri fileUri = FileProvider.getUriForFile(this, 
                    getString(R.string.file_provider_authority), outputFile);
            
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(fileUri, "application/pdf");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            
            if (intent.resolveActivity(getPackageManager()) != null) {
                startActivity(intent);
            } else {
                Toast.makeText(this, "No PDF viewer app found", Toast.LENGTH_SHORT).show();
            }
            
        } catch (Exception e) {
            Toast.makeText(this, "Error opening file: " + e.getMessage(), 
                          Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }
    }

    private void shareFile() {
        if (outputFile == null || !outputFile.exists()) {
            Toast.makeText(this, "No file to share", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            Uri fileUri = FileProvider.getUriForFile(this, 
                    getString(R.string.file_provider_authority), outputFile);
            
            Intent intent = new Intent(Intent.ACTION_SEND);
            intent.setType("application/pdf");
            intent.putExtra(Intent.EXTRA_STREAM, fileUri);
            intent.putExtra(Intent.EXTRA_SUBJECT, "Hybrid Bills - Orders with Thank You Leaflets");
            intent.putExtra(Intent.EXTRA_TEXT, 
                "Hybrid bills containing both cropped order labels and personalized thank-you leaflets for " + 
                extractedCustomers.size() + " customers.");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            
            Intent chooser = Intent.createChooser(intent, "Share Hybrid Bills PDF");
            if (chooser.resolveActivity(getPackageManager()) != null) {
                startActivity(chooser);
            } else {
                Toast.makeText(this, "No apps available to share", Toast.LENGTH_SHORT).show();
            }
            
        } catch (Exception e) {
            Toast.makeText(this, "Error sharing file: " + e.getMessage(), 
                          Toast.LENGTH_LONG).show();
            e.printStackTrace();
        }
    }

    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executorService != null && !executorService.isShutdown()) {
            executorService.shutdown();
        }
        
        // Clean up temporary files
        if (fileManager != null) {
            fileManager.cleanupTempFiles();
        }
    }
}
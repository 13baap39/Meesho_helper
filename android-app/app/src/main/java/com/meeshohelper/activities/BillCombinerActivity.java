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
import com.meeshohelper.utils.FileManager;
import com.meeshohelper.utils.PDFProcessor;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class BillCombinerActivity extends AppCompatActivity {

    private Button btnSelectFile, btnProcess, btnDownload, btnShare;
    private TextView tvSelectedFile, tvFileSize, tvProcessingStatus, tvProcessingDetails, tvResultInfo;
    private CardView cardProcessing;
    private LinearLayout layoutResults;
    private ProgressBar progressBar;

    private FileManager fileManager;
    private ExecutorService executorService;
    private ActivityResultLauncher<String[]> filePickerLauncher;

    private File selectedFile;
    private File outputFile;
    private int totalPages = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bill_combiner);

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
        tvResultInfo = findViewById(R.id.tvResultInfo);
        
        cardProcessing = findViewById(R.id.cardProcessing);
        layoutResults = findViewById(R.id.layoutResults);
        progressBar = findViewById(R.id.progressBar);
    }

    private void setupToolbar() {
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle(R.string.bill_combiner);
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
            String fileName = "selected_bill.pdf";
            
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
                    tvProcessingStatus.setText("Analyzing PDF structure...");
                    tvProcessingDetails.setText("Reading pages and preparing for cropping");
                });

                // Generate output filename
                String outputFileName = fileManager.generateOutputFilename(
                        selectedFile.getName(), "cropped_bills_4up");
                outputFile = new File(fileManager.getOutputDirectory(), outputFileName);

                runOnUiThread(() -> {
                    tvProcessingStatus.setText("Cropping and combining bills...");
                    tvProcessingDetails.setText("Creating 4-up layout");
                });

                // Create 4-up layout
                PDFProcessor.createFourUpLayout(selectedFile, outputFile);

                runOnUiThread(() -> {
                    showProcessingState(false);
                    showResults();
                    btnProcess.setEnabled(true);
                });

            } catch (Exception e) {
                runOnUiThread(() -> {
                    showProcessingState(false);
                    btnProcess.setEnabled(true);
                    Toast.makeText(BillCombinerActivity.this, 
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
        
        String resultText = "Bills successfully cropped and combined into 4-up layout";
        if (outputFile != null && outputFile.exists()) {
            String outputSize = FileManager.getReadableFileSize(outputFile.length());
            resultText += "\nOutput file size: " + outputSize;
        }
        
        tvResultInfo.setText(resultText);
        
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
            intent.putExtra(Intent.EXTRA_SUBJECT, "Cropped Bills - 4-up Layout");
            intent.putExtra(Intent.EXTRA_TEXT, "Cropped and combined bills in 4-up layout for easy printing.");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            
            Intent chooser = Intent.createChooser(intent, "Share Bills PDF");
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
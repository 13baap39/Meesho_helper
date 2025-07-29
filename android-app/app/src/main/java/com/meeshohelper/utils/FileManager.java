package com.meeshohelper.utils;

import android.content.Context;
import android.net.Uri;
import android.os.Environment;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class FileManager {
    private static final String APP_FOLDER = "MeeshoHelper";
    private static final String TEMP_FOLDER = "temp";
    private static final String OUTPUT_FOLDER = "output";

    private Context context;

    public FileManager(Context context) {
        this.context = context;
    }

    /**
     * Get the app's main directory in external storage
     */
    public File getAppDirectory() {
        File appDir = new File(context.getExternalFilesDir(null), APP_FOLDER);
        if (!appDir.exists()) {
            appDir.mkdirs();
        }
        return appDir;
    }

    /**
     * Get the temporary files directory
     */
    public File getTempDirectory() {
        File tempDir = new File(getAppDirectory(), TEMP_FOLDER);
        if (!tempDir.exists()) {
            tempDir.mkdirs();
        }
        return tempDir;
    }

    /**
     * Get the output files directory
     */
    public File getOutputDirectory() {
        File outputDir = new File(getAppDirectory(), OUTPUT_FOLDER);
        if (!outputDir.exists()) {
            outputDir.mkdirs();
        }
        return outputDir;
    }

    /**
     * Copy a file from URI to internal storage
     */
    public File copyFileFromUri(Uri sourceUri, String filename) throws IOException {
        File destFile = new File(getTempDirectory(), filename);
        
        try (InputStream inputStream = context.getContentResolver().openInputStream(sourceUri);
             OutputStream outputStream = new FileOutputStream(destFile)) {
            
            if (inputStream == null) {
                throw new IOException("Cannot open input stream from URI");
            }
            
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
            outputStream.flush();
        }
        
        return destFile;
    }

    /**
     * Generate a unique filename with timestamp
     */
    public String generateUniqueFilename(String prefix, String extension) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault());
        String timestamp = sdf.format(new Date());
        return prefix + "_" + timestamp + "." + extension;
    }

    /**
     * Generate output filename based on input filename and operation type
     */
    public String generateOutputFilename(String inputFilename, String operationType) {
        String baseName = inputFilename.replaceFirst("[.][^.]+$", ""); // Remove extension
        String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        return operationType + "_" + baseName + "_" + timestamp + ".pdf";
    }

    /**
     * Clean up temporary files
     */
    public void cleanupTempFiles() {
        File tempDir = getTempDirectory();
        if (tempDir.exists() && tempDir.isDirectory()) {
            File[] files = tempDir.listFiles();
            if (files != null) {
                for (File file : files) {
                    if (file.isFile()) {
                        file.delete();
                    }
                }
            }
        }
    }

    /**
     * Get file size in human readable format
     */
    public static String getReadableFileSize(long size) {
        if (size <= 0) return "0 B";
        
        final String[] units = new String[]{"B", "KB", "MB", "GB", "TB"};
        int digitGroups = (int) (Math.log10(size) / Math.log10(1024));
        
        return String.format(Locale.getDefault(), "%.1f %s", 
                size / Math.pow(1024, digitGroups), 
                units[digitGroups]);
    }

    /**
     * Check if external storage is available for read and write
     */
    public static boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED.equals(state);
    }

    /**
     * Check if external storage is available to at least read
     */
    public static boolean isExternalStorageReadable() {
        String state = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED.equals(state) ||
                Environment.MEDIA_MOUNTED_READ_ONLY.equals(state);
    }

    /**
     * Copy file from one location to another
     */
    public static void copyFile(File source, File destination) throws IOException {
        try (FileInputStream fis = new FileInputStream(source);
             FileOutputStream fos = new FileOutputStream(destination)) {
            
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, bytesRead);
            }
            fos.flush();
        }
    }
}
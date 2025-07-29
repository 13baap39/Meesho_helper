package com.meeshohelper;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.cardview.widget.CardView;
import androidx.core.content.ContextCompat;

import com.meeshohelper.activities.BillCombinerActivity;
import com.meeshohelper.activities.HybridBillActivity;
import com.meeshohelper.activities.LeafletGeneratorActivity;

public class MainActivity extends AppCompatActivity {

    private ActivityResultLauncher<String[]> permissionLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Setup toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Initialize permission launcher
        initializePermissionLauncher();

        // Check and request permissions
        checkAndRequestPermissions();

        // Setup card click listeners
        setupCardClickListeners();
    }

    private void initializePermissionLauncher() {
        permissionLauncher = registerForActivityResult(
                new ActivityResultContracts.RequestMultiplePermissions(),
                result -> {
                    boolean allGranted = true;
                    for (Boolean granted : result.values()) {
                        if (!granted) {
                            allGranted = false;
                            break;
                        }
                    }
                    
                    if (!allGranted) {
                        Toast.makeText(this, R.string.permission_denied, Toast.LENGTH_LONG).show();
                    }
                }
        );
    }

    private void checkAndRequestPermissions() {
        String[] permissions;
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ uses different permission model
            permissions = new String[]{
                    Manifest.permission.READ_MEDIA_IMAGES,
                    Manifest.permission.READ_MEDIA_VIDEO,
                    Manifest.permission.READ_MEDIA_AUDIO
            };
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+
            permissions = new String[]{
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.MANAGE_EXTERNAL_STORAGE
            };
        } else {
            // Android 10 and below
            permissions = new String[]{
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE
            };
        }

        boolean needsPermission = false;
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                needsPermission = true;
                break;
            }
        }

        if (needsPermission) {
            permissionLauncher.launch(permissions);
        }
    }

    private void setupCardClickListeners() {
        CardView cardLeaflet = findViewById(R.id.cardLeaflet);
        CardView cardBillCombiner = findViewById(R.id.cardBillCombiner);
        CardView cardHybrid = findViewById(R.id.cardHybrid);

        cardLeaflet.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, LeafletGeneratorActivity.class);
            startActivity(intent);
        });

        cardBillCombiner.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, BillCombinerActivity.class);
            startActivity(intent);
        });

        cardHybrid.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, HybridBillActivity.class);
            startActivity(intent);
        });
    }
}
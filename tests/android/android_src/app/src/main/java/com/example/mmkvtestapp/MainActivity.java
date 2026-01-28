package com.example.mmkvtestapp;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;

import com.tencent.mmkv.MMKV;

import java.io.File;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        String rootDir = MMKV.initialize(this);
        System.out.println("MMKV Root: " + rootDir);

        // Create ALL test data
        createTestData();
    }

    /// Creates ALL test data for ALL MMKV versions (e.g. 1.2.16, 1.3, 2.0, etc...).
    /// The onus is on the function to check compatibility with APIs (e.g. autokeyExpiration in v1.3)
    public void createTestData() {
        // All basic types encodings
        createDataAllTypes();

        // Int
        createInt32Keypair();
        createInt32KeypairWithRemove();
        createInt32KeypairWithUpdates();

        // Float
        createFloatKeypairWithUpdates();

        // String
        createStringKeypairWithRemove();
        createStringKeypairWithUpdates();

        // Encryption (AES-CFB)
        createDataEncrypt();
    }

    private void deleteMMKVFiles(String mmkvId) {
        File mmkvDir = new File(getFilesDir(), "mmkv");
        new File(mmkvDir, mmkvId).delete();
        new File(mmkvDir, mmkvId + ".crc").delete();
    }

    /// Create "data_all_types" MMKV file that uses basic API usage with all basic types
    private void createDataAllTypes() {
        // Delete MMKV and CRC file if it exists - want fresh slate
        deleteMMKVFiles("data_all_types");

        // Create MMKV file with all "basic" data types
        // int, long, float, double, string, bool, bytes
        MMKV kv = MMKV.mmkvWithID("data_all_types");
        kv.encode("int32_pkey", Integer.MAX_VALUE);
        kv.encode("int32_nkey", Integer.MIN_VALUE);
        kv.encode("int64_pkey", Long.MAX_VALUE);
        kv.encode("int64_nkey", Long.MIN_VALUE);
        kv.encode("bool_true_key", true);
        kv.encode("bool_false_key", false);
        kv.encode("string_key", "steven pak");
        kv.encode("bytes_key", "some bytes".getBytes(StandardCharsets.UTF_8));
        kv.encode("float_key", 3.14f);
        kv.encode("double_key", Double.MAX_VALUE);
    }

    private void createInt32Keypair() {
        deleteMMKVFiles("data_int32_keypair");

        MMKV kv = MMKV.mmkvWithID("data_int32_keypair");
        kv.encode("key", 4444);

        int value = kv.decodeInt("key");
        Log.d("MMKV", "key = " + value);
    }

    private void createInt32KeypairWithRemove() {
        deleteMMKVFiles("data_int32_keypair_with_remove");

        MMKV kv = MMKV.mmkvWithID("data_int32_keypair_with_remove");
        kv.encode("key", 4444);
        kv.removeValueForKey("key");

        int value = kv.decodeInt("key"); // default = 0
        Log.d("MMKV", "key after remove = " + value);
    }
    private void createInt32KeypairWithUpdates() {
        deleteMMKVFiles("data_int32_keypair_with_updates");

        MMKV kv = MMKV.mmkvWithID("data_int32_keypair_with_updates");
        kv.encode("int_key", 1);
        kv.encode("int_key", 10);
        kv.encode("int_key", 100);
        kv.encode("int_key", 1000);
    }
    private void createStringKeypairWithUpdates() {
        deleteMMKVFiles("data_string_keypair_with_updates");

        MMKV kv = MMKV.mmkvWithID("data_string_keypair_with_updates");
        kv.encode("string_key", "steven");
        kv.encode("string_key", "Ø");
        kv.encode("string_key", "𠜎");
        kv.encode("string_key", "😁");
    }
    private void createFloatKeypairWithUpdates() {
        deleteMMKVFiles("data_float_keypair_with_updates");

        MMKV kv = MMKV.mmkvWithID("data_float_keypair_with_updates");
        kv.encode("float_key", 3.14f);
        kv.encode("float_key", 3.141f);
        kv.encode("float_key", 3.1414f);
        kv.encode("float_key", 3.14141f);
    }
    private void createStringKeypairWithRemove() {
        deleteMMKVFiles("data_string_keypair_with_remove");

        MMKV kv = MMKV.mmkvWithID("data_string_keypair_with_remove");

        kv.encode("key", "old_1");
        kv.encode("key", "old_2");
        kv.encode("key", "old_3");
        kv.encode("key", "old_4");
        kv.encode("key", "old_5");
        kv.encode("key", "old_6");

        kv.removeValueForKey("key");

        kv.encode("key", "value_3");
        kv.encode("key", "value_4");
    }
    private void createDataEncrypt() {
        deleteMMKVFiles("data_encrypt");
        MMKV kv = MMKV.mmkvWithID(
                "data_encrypt",
                MMKV.SINGLE_PROCESS_MODE,
                "kindalongsecretkey"
        );
        kv.encode("bool_key", true);
        kv.encode("name", "steven");
        kv.encode("float_key", 3.14f);
        kv.encode("int_key", 42);
    }
}
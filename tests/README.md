# Sample data
This directory will contain various test files for different platforms and versions. For example:
- python/
  - version_1_2_13/
  - version_1_3/
- ios/
  - ...
- android/
  - v1_2_16/

See each platform-specific section for details on how I generated data, versioned that data, and tested the parser.
## Android
Within the `android/` directory, there is:
1. `android_src/` - this directory contains the Android source code I use to generate the MMKV test data. You _should_ be able to build the Android test application and run the application, which will generate the test data, but YMMV. To generate: 
   2. Go to `build.gradle` and ensure _only the version you want to exercise is imported_. For example, comment all but `implementation 'com.tencent:mmkv:1.2.16'` for exercising v1.2.16
   3. Sync Gradle
   4. Run the application, in which `MainActivity` will generate test data
   5. `adb shell` into your device and copy all the MMKV/CRC data from the `/data/data/com.example.mmkvtestapp/files/mmkv` directory
   6. Create a `<version>/` directory in the `android/` directory and move data there
2. `<version>/` - this directory will hold pure MMKV/CRC data from that specific version


## Python
I currently offer sample data created by `create_test_data.py`, which creates various MMKV databases with simple
usage of the API. This data was created on my M1 Macbook Pro 16" with the `python` library

The `create_test_data.py` requires a directory name to pipe the created test data. This is mainly for me capturing 
the evolution of the MMKV encoding over time (MMKV updates). 
1. Ensure you have the correct `MMKV` version installed (e.g. 1.2, 1.3.2)
2. Run:
```bash
# with 1.3 MMKV version installed
python util.py version_1_3

# with 1.2.13 MMKV version installed
python util.py v1_2_13
```

**NOTE**: To run the commands above, you need to ensure you have the correct `venv` with the version you're interested
in. I have different tags below to help me track.

### Versions

#### Pre v1.2.13
- I have data for `v1.2.13`, but the format is the same up to `v1.2.16`. The original visualizer I wrote was pointed to this serialization format.
- Corresponds https://github.com/spak9/mmkv_visualizer/releases/tag/v0.3.1

#### v1.3.2
- I have data for `v1.3.2`, but ths breaking change occured in `v1.3.0`.
- [v1.3.0](https://github.com/Tencent/MMKV/tree/v1.3.0?tab=readme-ov-file)
- [v1.3.0 Posix Wiki](https://github.com/Tencent/MMKV/wiki/python_setup/97d1c6e351a70554c26f2e09672463598243aca0)
  - It looks like they added auto-key expiration, which is likely a breaking change according to v1.3 release notes.
    
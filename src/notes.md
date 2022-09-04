# Notes/Research

## MMKV usage code flow (static analysis)

1. User must first "initialize" -
```c++
EX: initializeMMKV('/tmp/mmkv')
void MMKV::initializeMMKV(const MMKVPath_t &rootDir, MMKVLogLevel logLevel) {
    g_currentLogLevel = logLevel;

    ThreadLock::ThreadOnce(&once_control, initialize);

    g_rootDir = rootDir;
    mkPath(g_rootDir);

    MMKVInfo("root dir: " MMKV_PATH_FORMAT, g_rootDir.c_str());
}
```
The call to `mkPath()` looks like ultimately prepares a directory with all 777 permissions.
I think this sets up your working directory, with the actual MMKV file being made next.

2. Creating an MMKV file via a default constructor 
```c++

// #define DEFAULT_MMAP_ID "mmkv.default"
MMKV *MMKV::defaultMMKV(MMKVMode mode, string *cryptKey) {
#ifndef MMKV_ANDROID
    return mmkvWithID(DEFAULT_MMAP_ID, mode, cryptKey);
#else
    return mmkvWithID(DEFAULT_MMAP_ID, DEFAULT_MMAP_SIZE, mode, cryptKey);
#endif
}

...
...
...

EX: mmkvWithID('mmkv.default')
MMKV *MMKV::mmkvWithID(const string &mmapID, MMKVMode mode, string *cryptKey, MMKVPath_t *rootPath) {

    if (mmapID.empty()) {
        return nullptr;
    }
    SCOPED_LOCK(g_instanceLock);

    // Returns a string
    auto mmapKey = mmapedKVKey(mmapID, rootPath);

    //  g_instanceDic = new unordered_map<string, MMKV *>; --> A {string: MMKV} mapping for multiple MMKV instances in memory
    auto itr = g_instanceDic->find(mmapKey);
    if (itr != g_instanceDic->end()) {
        MMKV *kv = itr->second;
        return kv;
    }

    if (rootPath) {
        MMKVPath_t specialPath = (*rootPath) + MMKV_PATH_SLASH + SPECIAL_CHARACTER_DIRECTORY_NAME;
        if (!isFileExist(specialPath)) {
            mkPath(specialPath);
        }
        MMKVInfo("prepare to load %s (id %s) from rootPath %s", mmapID.c_str(), mmapKey.c_str(), rootPath->c_str());
    }

    // If it's a new MMKV or an existing MMKV file not in memory?
    auto kv = new MMKV(mmapID, mode, cryptKey, rootPath);
    kv->m_mmapKey = mmapKey;
    (*g_instanceDic)[mmapKey] = kv;
    return kv;
}
```

3. Setting data - according to the native C/C++ type, it will encode the data according to it's corresponding protobuf types

```c++
bool MMKV::set(bool value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbBoolSize();
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeBool(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(int32_t value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbInt32Size(value);
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeInt32(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(uint32_t value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbUInt32Size(value);
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeUInt32(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(int64_t value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbInt64Size(value);
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeInt64(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(uint64_t value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbUInt64Size(value);
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeUInt64(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(float value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbFloatSize();
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeFloat(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(double value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    size_t size = pbDoubleSize();
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
    output.writeDouble(value);

    return setDataForKey(move(data), key);
}

bool MMKV::set(const string &value, MMKVKey_t key) {
    if (isKeyEmpty(key)) {
        return false;
    }
    return setDataForKey(MMBuffer((void *) value.data(), value.length(), MMBufferNoCopy), key, true);
}
```

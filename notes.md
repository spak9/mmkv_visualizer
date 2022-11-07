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

## Encryption

The documentation notes the following in the FAQ:
```
What kind of encryption algorithm does MMKV use?
MMKV uses AES CFB-128 for encryption and decryption, using OpenSSL's implementation (version 1.1.0i). We choose CFB instead of widely used CBC, mainly because MMKV implements insert/update by an append-only operation. Stream encryption algorithms like CFB are more suitable.
```

EX:
```
String cryptKey = "My-Encrypt-Key";
MMKV kv = MMKV.mmkvWithID("MyID", MMKV.SINGLE_PROCESS_MODE, cryptKey);
```

### Inner workings

`using MMKVMapCrypt = std::unordered_map<std::string, mmkv::KeyValueHolderCrypt>;`
therefore has our typical mapping of {str: KeyValueHolderCrypt}

- We then construct an `MMKV` instance via the following logic:
```c++
if (cryptKey && cryptKey->length() > 0) {

        // an MMKVMapCrypt instance  -- basic map
        m_dicCrypt = new MMKVMapCrypt();

        // A AESCrypt instance initialized with the key bytes and the length of the key
        m_crypter = new AESCrypt(cryptKey->data(), cryptKey->length());
    } else {
        m_dic = new MMKVMap();
    }
```

The `m_crypter` instance is constructed as follows:
```c++
AESCrypt::AESCrypt(const void *key, size_t keyLength, const void *iv, size_t ivLength) {
    if (key && keyLength > 0) {
        // if key length is greater than 16, then default to 16.. guessing `memcpy` 
        // will fill in with NULL bytes if key 865167
        memcpy(m_key, key, (keyLength > AES_KEY_LEN) ? AES_KEY_LEN : keyLength);

        resetIV(iv, ivLength);

        // AES_KEY is a struct representing the round keys from the main key
        m_aesKey = new AES_KEY;
        memset(m_aesKey, 0, sizeof(AES_KEY));

        // Copies `m_key` which holds the user-inputted aes key into `m_aesKey`
        // eventually creating a struct that holds the AES round keys
        int ret = AES_set_encrypt_key(m_key, AES_KEY_BITSET_LEN, m_aesKey);
        MMKV_ASSERT(ret == 0);
    }
}
```

let's dive into the `doFullWriteBack` function for a deeper look at where the crytosystem 
is actually working.
```c++
bool MMKV::doFullWriteBack(pair<MMBuffer, size_t> preparedData, AESCrypt *newCrypter) {
    // get a pointer to the actual mmkv file data; offset 0
    auto ptr = (uint8_t *) m_file->getMemory();
    auto totalSize = preparedData.second;
#ifdef MMKV_IOS
    auto ret = guardForBackgroundWriting(ptr + Fixed32Size, totalSize);
    if (!ret.first) {
        return false;
    }
#endif

#ifndef MMKV_DISABLE_CRYPT
    uint8_t newIV[AES_KEY_LEN];

    // our "AESCryptor" instance with the current AES key 
    auto decrypter = m_crypter;

    // If we want to re-encrypt again with another key? 
    auto encrypter = (newCrypter == InvalidCryptPtr) ? nullptr : (newCrypter ? newCrypter : m_crypter);
    if (encrypter) {
        // If so, create a new IV
        AESCrypt::fillRandomIV(newIV);
        encrypter->resetIV(newIV, sizeof(newIV));
    }
#endif

    delete m_output;

    // Skip file size [0:4] bytes
    m_output = new CodedOutputData(ptr + Fixed32Size, m_file->getFileSize() - Fixed32Size);
#ifndef MMKV_DISABLE_CRYPT

    // BRANCH HERE!
    if (m_crypter) {
        memmoveDictionary(*m_dicCrypt, m_output, ptr, decrypter, encrypter, preparedData);
    } else {
#else
    {
        auto encrypter = m_crypter;
#endif
        memmoveDictionary(*m_dic, m_output, ptr, encrypter, totalSize);
    }

    m_actualSize = totalSize;
#ifndef MMKV_DISABLE_CRYPT
    if (encrypter) {
        recaculateCRCDigestWithIV(newIV);
    } else
#endif
    {
        recaculateCRCDigestWithIV(nullptr);
    }
    m_hasFullWriteback = true;
    // make sure lastConfirmedMetaInfo is saved
    sync(MMKV_SYNC);
    return true;
}
```

```c++
static void memmoveDictionary(MMKVMapCrypt &dic,            
                              CodedOutputData *output,
                              uint8_t *ptr,
                              AESCrypt *decrypter,
                              AESCrypt *encrypter,
                              pair<MMBuffer, size_t> &preparedData) {
    // reuse what's already in the file
    vector<KeyValueHolderCrypt *> vec;
    if (!dic.empty()) {
        // sort by offset
        vec.reserve(dic.size());
        for (auto &itr : dic) {
            if (itr.second.type == KeyValueHolderType_Offset) {
                vec.push_back(&itr.second);
            }
        }
        sort(vec.begin(), vec.end(), [](auto left, auto right) { return left->offset < right->offset; });
    }
    auto sizeHolder = ItemSizeHolder, sizeHolderSize = ItemSizeHolderSize;
    if (!vec.empty()) {
        auto smallestOffset = vec.front()->offset;
        if (smallestOffset != ItemSizeHolderSize && smallestOffset <= 5) {
            sizeHolderSize = smallestOffset;
            assert(sizeHolderSize != 0);
            static const uint32_t ItemSizeHolders[] = {0, 0x0f, 0xff, 0xffff, 0xffffff, 0xffffffff};
            sizeHolder = ItemSizeHolders[sizeHolderSize];
        }
    }
    output->writeRawVarint32(static_cast<int32_t>(sizeHolder));
    auto writePtr = output->curWritePointer();
    if (encrypter) {
        encrypter->encrypt(writePtr - sizeHolderSize, writePtr - sizeHolderSize, sizeHolderSize);
    }
    if (!vec.empty()) {
        // merge nearby items to make memmove quicker
        vector<tuple<uint32_t, uint32_t, AESCryptStatus *>> dataSections; // pair(offset, size)
        dataSections.push_back(vec.front()->toTuple());
        for (size_t index = 1, total = vec.size(); index < total; index++) {
            auto kvHolder = vec[index];
            auto &lastSection = dataSections.back();
            if (kvHolder->offset == get<0>(lastSection) + get<1>(lastSection)) {
                get<1>(lastSection) += kvHolder->pbKeyValueSize + kvHolder->keySize + kvHolder->valueSize;
            } else {
                dataSections.push_back(kvHolder->toTuple());
            }
        }
        // do the move
        auto basePtr = ptr + Fixed32Size;
        for (auto &section : dataSections) {
            auto crypter = decrypter->cloneWithStatus(*get<2>(section));
            crypter.decrypt(basePtr + get<0>(section), writePtr, get<1>(section));
            writePtr += get<1>(section);
        }
        // update offset & AESCryptStatus
        if (encrypter) {
            auto offset = sizeHolderSize;
            for (auto kvHolder : vec) {
                kvHolder->offset = offset;
                auto size = kvHolder->pbKeyValueSize + kvHolder->keySize + kvHolder->valueSize;
                encrypter->getCurStatus(kvHolder->cryptStatus);
                encrypter->encrypt(basePtr + offset, basePtr + offset, size);
                offset += size;
            }
        }
    }
    auto &data = preparedData.first;
    if (data.length() > 0) {
        auto dataSize = CodedInputData(data.getPtr(), data.length()).readUInt32();
        if (dataSize > 0) {
            auto dataPtr = (uint8_t *) data.getPtr() + pbRawVarint32Size(dataSize);
            if (encrypter) {
                encrypter->encrypt(dataPtr, writePtr, dataSize);
            } else {
                memcpy(writePtr, dataPtr, dataSize);
            }
            writePtr += dataSize;
        }
    }
    auto writtenSize = static_cast<size_t>(writePtr - output->curWritePointer());
    assert(writtenSize + sizeHolderSize == preparedData.second);
    output->seek(writtenSize);
}
```


























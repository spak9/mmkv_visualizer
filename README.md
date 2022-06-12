# mmkv_visualizer
A web application that will allow you to visualize LevelDB databases, with all processing done client-side.

## Analysis

The following will be an early analysis on the protocol, statically analyzing the C++ source code.


The MMKV class is defined as the following:
```C++
MMKV::MMKV(const string &mmapID, MMKVMode mode, string *cryptKey, MMKVPath_t *rootPath)
    : m_mmapID(mmapID)                                          // Unique string ID for MMKV instance
    , m_path(mappedKVPathWithID(m_mmapID, mode, rootPath))
    , m_crcPath(crcPathWithID(m_mmapID, mode, rootPath))
    , m_dic(nullptr)
    , m_dicCrypt(nullptr)
    , m_file(new MemoryFile(m_path))
    , m_metaFile(new MemoryFile(m_crcPath))
    , m_metaInfo(new MMKVMetaInfo())
    , m_crypter(nullptr)
    , m_lock(new ThreadLock())
    , m_fileLock(new FileLock(m_metaFile->getFd()))
    , m_sharedProcessLock(new InterProcessLock(m_fileLock, SharedLockType))
    , m_exclusiveProcessLock(new InterProcessLock(m_fileLock, ExclusiveLockType))
    , m_isInterProcess((mode & MMKV_MULTI_PROCESS) != 0) {
    m_actualSize = 0;
    m_output = nullptr;

#    ifndef MMKV_DISABLE_CRYPT
    if (cryptKey && cryptKey->length() > 0) {
        m_dicCrypt = new MMKVMapCrypt();
        m_crypter = new AESCrypt(cryptKey->data(), cryptKey->length());
    } else {
        m_dic = new MMKVMap();
    }
#    else
    m_dic = new MMKVMap();
#    endif

    m_needLoadFromFile = true;
    m_hasFullWriteback = false;

    m_crcDigest = 0;

    m_lock->initialize();
    m_sharedProcessLock->m_enable = m_isInterProcess;
    m_exclusiveProcessLock->m_enable = m_isInterProcess;

    // sensitive zone
    {
        SCOPED_LOCK(m_sharedProcessLock);
        loadFromFile();
    }
}
#endif
```

1. First must initialize the database
```python
import mmkv
if __name__ == '__main__':
    mmkv.MMKV.initializeMMKV('/tmp/mmkv')
```

2. mmkvWithId()
```C++
MMKV *MMKV::mmkvWithID(const string &mmapID, MMKVMode mode, string *cryptKey, MMKVPath_t *rootPath) {

    // either a user-given mmapID string will be given OR a default value
    if (mmapID.empty()) {
        return nullptr;
    }
    SCOPED_LOCK(g_instanceLock);

    // Seems to return a string that serves as a unique identifier for a specific "MMKV *" instance.
    // the "mmapedKVKey()" function seems to return either the mmapID or the md5() of the concat of
    // multiple string elements.
    auto mmapKey = mmapedKVKey(mmapID, rootPath);
    
    // "g_instanceDic" is a dictionary that maps {<mmkv_ids> : MMKV instance}.
    // The following the declaration: "unordered_map<string, MMKV *> *g_instanceDic"
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

    auto kv = new MMKV(mmapID, mode, cryptKey, rootPath);
    kv->m_mmapKey = mmapKey;
    (*g_instanceDic)[mmapKey] = kv;
    return kv;
}
```

```
string mmapedKVKey(const string &mmapID, const MMKVPath_t *rootPath) {
    if (rootPath && g_rootDir != (*rootPath)) {
        return md5(*rootPath + MMKV_PATH_SLASH + string2MMKVPath_t(mmapID));
    }
    return mmapID;
}
```

## Setting data

By this time, we'll have a `MMKV *kv` instance. This class has the typical `set(T value, string key)`.
Let's view a example set():
```C++
// Takes in a `int32_t` value, which can a signed value. 
bool MMKV::set(int32_t value, MMKVKey_t key) {
    
    if (isKeyEmpty(key)) {
    
        return false;
    }// Pass in key The value cannot be an empty string 
    
    // Returns the number of bytes needed to base-128 encode a 32-bit int. 
    // Note: May return 10 if `value` is negative
    size_t size = pbInt32Size(value);
    
    // Prepare a buffer of `size` length 
    MMBuffer data(size);
    CodedOutputData output(data.getPtr(), size);
   
    // Writes the `value` as a Int32 within the protobuf-encoding scheme (wire type 0 - varint "int32")
    output.writeInt32(value);

    // Call `setDataForKey(CodedOutputData_ref, "test_key")
    return setDataForKey(move(data), key);
}
```

From the programmer's perspective, the call is done and now the key-value is now saved and ready
for usability via "get()". However, there's still more information to be gained regarding how the 
protobuf-encoded buffer is serialized to disk.
Let's take a look at `setDataForKey(CodedOutputData_ref, "test_key")`

```C++
// eg. `setDataForKey(CodedOutputData_ref, "test_key", False)`

bool MMKV::setDataForKey(MMBuffer &&data, MMKVKey_t key, bool isDataHolder) {
    
    if ((!isDataHolder && data.length() == 0) || isKeyEmpty(key)) {
    
        return false;
    }
    SCOPED_LOCK(m_lock);
    SCOPED_LOCK(m_exclusiveProcessLock);
    checkLoadData();

// ! ALL SKIPPED FOR VANILLA ENCODING - deep dive needed for encryption use cases !)
[//]: # (#ifndef MMKV_DISABLE_CRYPT)

[//]: # (    

[//]: # (    if &#40;m_crypter&#41; {)

[//]: # (    )
[//]: # (        if &#40;isDataHolder&#41; {)

[//]: # (    )
[//]: # (            auto sizeNeededForData = pbRawVarint32Size&#40;&#40;uint32_t&#41; data.length&#40;&#41;&#41; + data.length&#40;&#41;;)

[//]: # (            if &#40;!KeyValueHolderCrypt::isValueStoredAsOffset&#40;sizeNeededForData&#41;&#41; {)

[//]: # (    )
[//]: # (                data = MiniPBCoder::encodeDataWithObject&#40;data&#41;;// take value Construct a Protobuf Data objects )

[//]: # (                isDataHolder = false;)

[//]: # (            })

[//]: # (        })

[//]: # (        auto itr = m_dicCrypt->find&#40;key&#41;;)

[//]: # (        if &#40;itr != m_dicCrypt->end&#40;&#41;&#41; {)

[//]: # (    )
[//]: # (# ifdef MMKV_APPLE)

[//]: # (            auto ret = appendDataWithKey&#40;data, key, itr->second, isDataHolder&#41;;)

[//]: # (# else)

[//]: # (			// Save data logic )

[//]: # (            auto ret = appendDataWithKey&#40;data, key, isDataHolder&#41;;)

[//]: # (# endif)

[//]: # (            if &#40;!ret.first&#41; {)

[//]: # (    )
[//]: # (                return false;)

[//]: # (            })

[//]: # (            if &#40;KeyValueHolderCrypt::isValueStoredAsOffset&#40;ret.second.valueSize&#41;&#41; {)

[//]: # (    )
[//]: # (                KeyValueHolderCrypt kvHolder&#40;ret.second.keySize, ret.second.valueSize, ret.second.offset&#41;;)

[//]: # (                memcpy&#40;&kvHolder.cryptStatus, &t_status, sizeof&#40;t_status&#41;&#41;;)

[//]: # (                itr->second = move&#40;kvHolder&#41;;)

[//]: # (            } else {)

[//]: # (    )
[//]: # (                itr->second = KeyValueHolderCrypt&#40;move&#40;data&#41;&#41;;)

[//]: # (            })

[//]: # (        } else {)

[//]: # (    )
[//]: # (            auto ret = appendDataWithKey&#40;data, key, isDataHolder&#41;;)

[//]: # (            if &#40;!ret.first&#41; {)

[//]: # (    )
[//]: # (                return false;)

[//]: # (            })

[//]: # (            if &#40;KeyValueHolderCrypt::isValueStoredAsOffset&#40;ret.second.valueSize&#41;&#41; {)

[//]: # (    )
[//]: # (                auto r = m_dicCrypt->emplace&#40;)

[//]: # (                    key, KeyValueHolderCrypt&#40;ret.second.keySize, ret.second.valueSize, ret.second.offset&#41;&#41;;)

[//]: # (                if &#40;r.second&#41; {)

[//]: # (    )
[//]: # (                    memcpy&#40;&&#40;r.first->second.cryptStatus&#41;, &t_status, sizeof&#40;t_status&#41;&#41;;)

[//]: # (                })

[//]: # (            } else {)

[//]: # (    )
[//]: # (                m_dicCrypt->emplace&#40;key, KeyValueHolderCrypt&#40;move&#40;data&#41;&#41;&#41;;)

[//]: # (            })

[//]: # (        })

[//]: # (    } else)

[//]: # (#endif // MMKV_DISABLE_CRYPT)
    {
    
        // Firstly, "m_dic" is an instance of the following `MMKVMap = std::unordered_map<std::string, mmkv::KeyValueHolder>;`
        // Therefore, it's just a map/dictionary of key strings to some MMBuffer/KeyValueHolder
        auto itr = m_dic->find(key);
        if (itr != m_dic->end()) {
    
            auto ret = appendDataWithKey(data, itr->second, isDataHolder);
            if (!ret.first) {
    
                return false;
            }
            itr->second = std::move(ret.second);
        } else {
    
            
            auto ret = appendDataWithKey(data, key, isDataHolder);
            if (!ret.first) {
    
                return false;
            }
            m_dic->emplace(key, std::move(ret.second));// and insert similar   It's just emplace  The biggest effect is to avoid unnecessary temporary variables 
        }
    }
    m_hasFullWriteback = false;
#ifdef MMKV_APPLE
    [key retain];
#endif
    return true;
}
```



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

- By this time, we'll have a `MMKV *kv` instance. This class has the typical `set(T value, string key)`.
Let's view a example set():
```C++
// Takes in a "char *value" which is basically a string and a "MMKVKey_t key" which is basically a 
// string type or a "NSString *" on Apple.
bool MMKV::set(const char *value, MMKVKey_t key) {
    if (!value) {
        removeValueForKey(key);
        return true;
    }
    return setDataForKey(MMBuffer((void *) value, strlen(value), MMBufferNoCopy), key, true);
}```

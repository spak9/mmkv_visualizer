# MMKV Reverse Engineering Notes
Some basic notes I took while trying to understand the data serialization. I don't program in C++, so understand that...

## Breaking Changes
There seems to be 3 major versions of the MMKV library that have breaking changes with respect to the serialization:
1. <= v1.2.16 - This is the version I made the visualizer for originally
2. v1.3.0 - This version introduced `Auto Expiration`. This is an upgradable feature.
3. v2.0.0 - This was a new major change.

The CRC files that were serialized on-disk as result of when the `MMKVMetaInfo` is written to the `.crc` file byte-for-byte
via the `memcpy`/`write` operation. However, you can see changes in the CRC format:

```c++
// v1.3.0
struct MMKVMetaInfo {
    uint32_t m_crcDigest = 0;
    uint32_t m_version = MMKVVersionSequence;
    uint32_t m_sequence = 0; // full write-back count
    uint8_t m_vector[AES_KEY_LEN] = {};
    uint32_t m_actualSize = 0;

    // confirmed info: it's been synced to file
    struct {
        uint32_t lastActualSize = 0;
        uint32_t lastCRCDigest = 0;
        uint32_t _reserved[16] = {};
    } m_lastConfirmedMetaInfo;

    ///// THIS SNIPPET
    uint64_t m_flags = 0;

    enum MMKVMetaInfoFlag : uint64_t {
        EnableKeyExipre = 1 << 0,
    };
    bool hasFlag(MMKVMetaInfoFlag flag) { return (m_flags & flag) != 0; }
    void setFlag(MMKVMetaInfoFlag flag) { m_flags |= flag; }
    void unsetFlag(MMKVMetaInfoFlag flag) { m_flags &= ~flag; }
    /////

    void write(void *ptr) const {
        MMKV_ASSERT(ptr);
        memcpy(ptr, this, sizeof(MMKVMetaInfo));
    }

    void writeCRCAndActualSizeOnly(void *ptr) const {
        MMKV_ASSERT(ptr);
        auto other = (MMKVMetaInfo *) ptr;
        other->m_crcDigest = m_crcDigest;
        other->m_actualSize = m_actualSize;
    }

    void read(const void *ptr) {
        MMKV_ASSERT(ptr);
        memcpy(this, ptr, sizeof(MMKVMetaInfo));
    }
};
```
As you can see the addition of the `uint64_t m_flags` value to represent the new `MMKVMetaInfoFlag`. That is at 
offset 104, therefore we should be able to detect whether the library is _at least_ on v1.3.0 or above.
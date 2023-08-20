# Sample data and python tests
This contains example test data created with the `mmkv` python package, available from Tencent's MMKV repo on Github. 

I currently offer sample data created by `create_test_data.py`, which creates various MMKV databases with simple
usage of the API (eg. CRUD operations). This data was created on my M1 Macbook Pro 16" with the `Posix` library.
The `create_test_data.py` requires a directory name to pipe the created test data. This is mainly for me capturing 
the evolution of the the MMKV serialization encoding over time (MMKV updates).
```python
python create_test_data.py version_1_3
```

To capture any evolving serialization formats, I create specific directories according to the python MMKV version.
For example, `version_1_2_13` should contain test data from v1.2.13.
It also contains a python script for testing the test data.
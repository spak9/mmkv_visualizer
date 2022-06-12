from pathlib import Path

class MMKVParser:
    """

    """

    def __init__(self):
        self._mmkv_buffer = None
        self._crc_buffer = None


    def initialize(self, mmkv_file_name: str, crc_file_name: str = ''):
        """
        Sets up the mmkv data file and optionally the CRC32 file.
        If crc filename is not given, will attempt to use append ".crc"

        :param mmkv_file_name: filename string
        :param crc_file_name: filename string
        :return: None
        """
        # Check if files exists
        mmkv_file_path = Path(f'../data/{mmkv_file_name}')
        if not mmkv_file_path.exists():
            print('test data is not found')
            exit(1)

        # TODO - CRC32 check


        # Open and read mmkv file data
        self._mmkv_buffer = open(mmkv_file_path, 'rb').read()
        print(self._mmkv_buffer)





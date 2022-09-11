"""
Not a typical `pip` requirements file, but a file that acts as the python standard libraries
that we need to import in `runPython` with Pyodide
"""
from io import BufferedIOBase, BytesIO
from pathlib import Path
from typing import Optional, List, Tuple, Union
from collections import defaultdict

import sys
import struct
import ctypes

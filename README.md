# mmkv_visualizer
A web application that will allow you to visualize [MMKV](https://github.com/Tencent/MMKV) databases, with all processing done client-side.
The [web service](https://www.mmkv-visualizer.com/) utilizes [Pyodide](https://pyodide.org/en/stable/) which enables a python 
runtime within the browser, in which the main MMKV parsing code is written in.
*It sends no data up to any server and all the parsing happens right in your browser.*

## Usage

There are three ways you can use the following code:

1. Web Application:

The main way is to utilize the online web service provided at https://www.mmkv-visualizer.com/.
You can simply drag & drop or choose an MMKV of your choice, then visualize the data.
The visualizer allows you to iterate through different data type encodings, including strings, 
bytes, NSCodings, and more. 
You can iterate the type by simply clicking a table cell, as well as expand the data to get a deeper look.

See below for more information on decryption capabilities.

2. Local Web Application:

For those who would like to run the service locally, all you need is `npm`:
- `cd frontend`
- `npm install`
- `npm run dev`

3. Python Parsing:

If you'd like to use only the python code to parse the data itself, the parsing code can be found [here](https://github.com/spak9/mmkv_visualizer/blob/main/frontend/public/mmkv_parser.py).
The main advantage of using this parsing code over the official python wrapper is that the official python wrapper
does not allow you to see older data, while this parser can. This may be important for the inclined forensicator. 

You can also find a set of python tests found at `tests`.

## Decryption

The MMKV library natives allows users to encrypt their MMKV files using AES-128 in CFB mode.
If needed, the application allows decryption of the data, but must be given the following:

1. The encrypted MMKV file AND corresponding .crc file (the .crc file contains the 16-byte IV)
2. The AES key. (Will be prompted to enter the AES key in the form of a hexstring, allowing any length for the key)

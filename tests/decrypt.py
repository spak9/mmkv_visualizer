from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes 

if __name__ == "__main__":

	metadata = open('create_string_keypair_with_encrypt.crc', 'rb').read()
	data = open('create_string_keypair_with_encrypt', 'rb').read()[4:4 + 0x11]
	key = b'key\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	iv = metadata[12:12 + 16]

	cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
	decryptor = cipher.decryptor()

	res = decryptor.update(data) + decryptor.finalize()
	print(res)
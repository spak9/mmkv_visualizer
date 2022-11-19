// Prepare functionality for converting [ArrayBuffer] to hex string
const byteToHex = [];
for (let n = 0; n <= 0xff; ++n)
{
  const hexOctet = n.toString(16).padStart(2, "0");
  byteToHex.push(hexOctet);
}

// Converts an `arrayBuffer` into a hex string
export function hex(arrayBuffer)
{
  const buff = new Uint8Array(arrayBuffer);
  const hexOctets = [];
  for (let i = 0; i < buff.length; ++i)
    hexOctets.push(byteToHex[buff[i]]);

  return hexOctets.join("");
}

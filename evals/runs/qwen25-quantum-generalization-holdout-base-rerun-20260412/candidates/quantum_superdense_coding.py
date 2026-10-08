def encode_message(bits):
    encoded_bits = ""
    for i in range(2):
        if bits[i] == '0':
            encoded_bits += '0'
        else:
            encoded_bits += '1'
    return encoded_bits

def decode_message(encoded_bits):
    decoded_bits = ''
    for bit in encoded_bits:
        if bit == '0':
            decoded_bits += '0'
        elif bit == '1':
            decoded_bits += '1'
    return decoded_bits

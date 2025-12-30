import base64
import string
import re

def is_printable(s):
    return all(c in string.printable for c in s)

def find_base64_in_text(text, min_length=8):
    base64_pattern = r'[A-Za-z0-9+/]{' + str(min_length) + r',}={0,2}'
    candidates = re.findall(base64_pattern, text)
    print(f"[DEBUG] Total kandidat base64 ditemukan oleh regex: {len(candidates)}")

    found = []
    for candidate in candidates:
        try:
            decoded_bytes = base64.b64decode(candidate, validate=True)
            decoded_text = decoded_bytes.decode('utf-8')
            if is_printable(decoded_text):
                found.append((candidate, decoded_text))
        except Exception:
            continue

    return found

def main():
    input_file = 'Windows_Logs.xml'
    output_file = 'hasil_deteksi.txt'

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    results = find_base64_in_text(text)

    if results:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{len(results)} base64 string ditemukan:\n\n")
            for i, (encoded, decoded) in enumerate(results, 1):
                f.write(f"#{i}\nEncoded: {encoded}\nDecoded: {decoded}\n\n")
        print(f"{len(results)} base64 string valid disimpan di '{output_file}'")
    else:
        print("Tidak ditemukan base64 encoded string yang valid.")

if __name__ == '__main__':
    main()

    
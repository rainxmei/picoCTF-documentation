import base64
import string
import re
import argparse

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
    parser = argparse.ArgumentParser(
        description='Deteksi dan decode base64 string dari file teks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Contoh penggunaan:
  python script.py -i Windows_Logs.xml -o hasil.txt
  python script.py -i data.txt -o output.txt -m 16
  python script.py -i logs.xml -o hasil.txt -v
        '''
    )
    
    parser.add_argument('-i', '--input', 
                        required=True,
                        help='File input yang akan dianalisis')
    
    parser.add_argument('-o', '--output', 
                        default='hasil_deteksi.txt',
                        help='File output untuk menyimpan hasil (default: hasil_deteksi.txt)')
    
    parser.add_argument('-m', '--min-length', 
                        type=int, 
                        default=8,
                        help='Panjang minimum string base64 (default: 8)')
    
    parser.add_argument('-v', '--verbose', 
                        action='store_true',
                        help='Tampilkan hasil di console juga')
    
    parser.add_argument('-e', '--encoding', 
                        default='utf-8',
                        help='Encoding file input (default: utf-8)')

    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding=args.encoding) as f:
            text = f.read()
        print(f"[INFO] File '{args.input}' berhasil dibaca")
    except FileNotFoundError:
        print(f"[ERROR] File '{args.input}' tidak ditemukan!")
        return
    except Exception as e:
        print(f"[ERROR] Gagal membaca file: {e}")
        return

    results = find_base64_in_text(text, min_length=args.min_length)

    if results:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"{len(results)} base64 string ditemukan:\n\n")
                for i, (encoded, decoded) in enumerate(results, 1):
                    output_text = f"#{i}\nEncoded: {encoded}\nDecoded: {decoded}\n\n"
                    f.write(output_text)
                    
                    if args.verbose:
                        print(output_text)
            
            print(f"[SUCCESS] {len(results)} base64 string valid disimpan di '{args.output}'")
        except Exception as e:
            print(f"[ERROR] Gagal menulis file output: {e}")
    else:
        print("[INFO] Tidak ditemukan base64 encoded string yang valid.")

if __name__ == '__main__':
    main()
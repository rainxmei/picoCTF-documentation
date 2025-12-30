#!/usr/bin/env python3
import argparse
from PIL import Image
import sys

def extract_bits(pixel_value, bit_positions):
    """
    Extract specific bits from a pixel value.
    bit_positions: string of 8 chars, '1' means extract that bit, '0' means skip
    Example: '10000000' extracts MSB, '00000001' extracts LSB
    """
    binary = format(pixel_value, '08b')
    extracted = []
    
    for i, should_extract in enumerate(bit_positions):
        if should_extract == '1':
            extracted.append(binary[i])
    
    return extracted

def decode_image(input_file, output_file, bit_pattern, channel_order='RGB', extract_mode='column'):
    """
    Decode hidden data from an image using steganography.
    
    Args:
        input_file: Path to input image
        output_file: Path to output text file
        bit_pattern: 8-character string indicating which bits to extract (e.g., '10000000' for MSB)
        channel_order: Order to read RGB channels (default: 'RGB')
        extract_mode: 'column' or 'row' traversal (default: 'column')
    """
    try:
        img = Image.open(input_file)
        width, height = img.size
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        binary_data = []
        
        # Determine traversal pattern
        if extract_mode == 'row':
            coordinates = [(x, y) for y in range(height) for x in range(width)]
        else:  # column
            coordinates = [(x, y) for x in range(width) for y in range(height)]
        
        # Extract bits from each pixel
        for x, y in coordinates:
            pixel = img.getpixel((x, y))
            
            # Extract bits from each channel based on order
            channel_data = {}
            channel_data['R'] = extract_bits(pixel[0], bit_pattern)
            channel_data['G'] = extract_bits(pixel[1], bit_pattern)
            channel_data['B'] = extract_bits(pixel[2], bit_pattern)
            
            # Add bits in specified channel order
            for channel in channel_order.upper():
                binary_data.extend(channel_data[channel])
        
        # Convert binary to ASCII text
        output_text = []
        for i in range(0, len(binary_data) - 7, 8):
            byte = ''.join(binary_data[i:i+8])
            ascii_val = int(byte, 2)
            
            # Only include printable ASCII characters
            if 32 <= ascii_val <= 126:
                output_text.append(chr(ascii_val))
            elif ascii_val == 10 or ascii_val == 13:  # newline or carriage return
                output_text.append(chr(ascii_val))
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(output_text))
        
        print(f"✓ Successfully decoded {input_file}")
        print(f"✓ Output saved to {output_file}")
        print(f"✓ Extracted {len(output_text)} characters")
        
    except FileNotFoundError:
        print(f"✗ Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        prog='StegoDecode',
        description='Steganography decoder for extracting hidden data from images using MSB/LSB techniques',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Extract MSB (Most Significant Bit):
    python stego.py -i hidden.png -o output.txt -b 10000000
  
  Extract LSB (Least Significant Bit):
    python stego.py -i hidden.png -o output.txt -b 00000001
  
  Extract 2 LSBs with custom channel order:
    python stego.py -i hidden.png -o output.txt -b 00000011 -c BGR
  
  Extract using row traversal:
    python stego.py -i hidden.png -o output.txt -b 10000000 -m row
        '''
    )
    
    parser.add_argument('-i', '--input',
                        required=True,
                        help='Input image file (PNG, JPG, etc.)')
    
    parser.add_argument('-o', '--output',
                        required=True,
                        help='Output text file for decoded message')
    
    parser.add_argument('-b', '--bits',
                        default='00000001',
                        help='Bit pattern to extract (8 chars: 1=extract, 0=skip). '
                             'Examples: "10000000" for MSB, "00000001" for LSB (default: %(default)s)')
    
    parser.add_argument('-c', '--channels',
                        default='RGB',
                        choices=['RGB', 'RBG', 'GRB', 'GBR', 'BRG', 'BGR'],
                        help='Channel order for extraction (default: %(default)s)')
    
    parser.add_argument('-m', '--mode',
                        default='column',
                        choices=['column', 'row'],
                        help='Pixel traversal mode (default: %(default)s)')
    
    args = parser.parse_args()
    
    # Validate bit pattern
    if len(args.bits) != 8 or not all(c in '01' for c in args.bits):
        print("✗ Error: Bit pattern must be exactly 8 characters of '0' or '1'", file=sys.stderr)
        sys.exit(1)
    
    if args.bits == '00000000':
        print("✗ Error: Bit pattern must have at least one '1'", file=sys.stderr)
        sys.exit(1)
    
    # Run decoder
    decode_image(args.input, args.output, args.bits, args.channels, args.mode)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  SHADOW - Advanced Steganography Tool                        ║
║  Hide text, files & images inside images                    ║
║  Author: mohmmadsedeg30-design                               ║
║  GitHub: https://github.com/mohmmadsedeg30-design/shadow    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import zlib
import base64
import argparse
from pathlib import Path
from PIL import Image
import numpy as np
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import struct

__version__ = "2.1.0"
__author__ = "mohmmadsedeg30-design"

# ═══════════════════════════════════════════════════════════════
# Terminal Colors
# ═══════════════════════════════════════════════════════════════
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    DARK = '\033[90m'

# ═══════════════════════════════════════════════════════════════
# ASCII Logo
# ═══════════════════════════════════════════════════════════════
LOGO = f"""
{Colors.DARK}     ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
     ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
     ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
     ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
     ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝{Colors.END}
{Colors.CYAN}              ═══ Advanced Steganography Tool ═══{Colors.END}
{Colors.DARK}              [ Hide Secrets In Plain Sight ]{Colors.END}
{Colors.YELLOW}              Version: {__version__} | By: {__author__}{Colors.END}
"""

# ═══════════════════════════════════════════════════════════════
# Crypto Engine (AES-256 via Fernet)
# ═══════════════════════════════════════════════════════════════
class CryptoEngine:
    """Encryption Engine - Protects data before hiding"""

    @staticmethod
    def _derive_key(password: str, salt: bytes = None) -> tuple:
        """Derive strong key from password"""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt(data: bytes, password: str) -> bytes:
        """Encrypt data"""
        key, salt = CryptoEngine._derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(data)
        return salt + encrypted

    @staticmethod
    def decrypt(data: bytes, password: str) -> bytes:
        """Decrypt data"""
        salt = data[:16]
        encrypted = data[16:]
        key, _ = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted)

# ═══════════════════════════════════════════════════════════════
# Stegano Engine (LSB - Least Significant Bit)
# ═══════════════════════════════════════════════════════════════
class SteganoEngine:
    """LSB Steganography Engine"""

    SIGNATURE = b'SHADOW\x00'
    VERSION = b'\x02'

    @staticmethod
    def _bytes_to_bits(data: bytes) -> str:
        return ''.join(format(byte, '08b') for byte in data)

    @staticmethod
    def _bits_to_bytes(bits: str) -> bytes:
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    @staticmethod
    def _create_header(data_len: int, is_encrypted: bool, data_type: str) -> bytes:
        type_map = {'text': 0, 'file': 1, 'image': 2}
        type_byte = type_map.get(data_type, 1)
        flags = 0x01 if is_encrypted else 0x00

        header = struct.pack('>7sBIB', 
            SteganoEngine.SIGNATURE,
            SteganoEngine.VERSION[0],
            data_len,
            (flags << 4) | type_byte
        )
        return header

    @staticmethod
    def _parse_header(header: bytes) -> dict:
        sig, ver, data_len, flags_type = struct.unpack('>7sBIB', header)
        return {
            'signature': sig,
            'version': ver,
            'data_length': data_len,
            'is_encrypted': bool((flags_type >> 4) & 0x01),
            'data_type': ['text', 'file', 'image'][flags_type & 0x0F]
        }

    @classmethod
    def hide(cls, cover_path: str, secret_path: str, output_path: str, 
             password: str = None, data_type: str = 'file') -> bool:
        try:
            img = Image.open(cover_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)
            height, width, channels = pixels.shape
            max_capacity = height * width * channels // 8

            if data_type == 'text' and not os.path.exists(secret_path):
                secret_data = secret_path.encode('utf-8')
            else:
                with open(secret_path, 'rb') as f:
                    secret_data = f.read()

            compressed = zlib.compress(secret_data, level=9)

            is_encrypted = False
            if password:
                compressed = CryptoEngine.encrypt(compressed, password)
                is_encrypted = True

            header = cls._create_header(len(compressed), is_encrypted, data_type)
            full_data = header + compressed

            needed_bits = len(full_data) * 8
            if needed_bits > max_capacity:
                raise ValueError(
                    f"Image too small! Capacity: {max_capacity} bytes, "
                    f"Required: {len(full_data)} bytes"
                )

            bits = cls._bytes_to_bits(full_data)
            flat_pixels = pixels.flatten()
            for i, bit in enumerate(bits):
                flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(bit)

            new_pixels = flat_pixels.reshape(height, width, channels)
            new_img = Image.fromarray(new_pixels.astype('uint8'))
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            new_img.save(output_path, 'PNG')

            return True

        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
            return False

    @classmethod
    def extract(cls, stego_path: str, output_path: str = None, password: str = None) -> dict:
        try:
            img = Image.open(stego_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)

            flat_pixels = pixels.flatten()
            bits = ''.join(str(pixel & 1) for pixel in flat_pixels)
            all_bytes = cls._bits_to_bytes(bits)

            sig_idx = all_bytes.find(cls.SIGNATURE)
            if sig_idx == -1:
                raise ValueError("No hidden data found in this image!")

            header = all_bytes[sig_idx:sig_idx + 13]
            info = cls._parse_header(header)

            data_start = sig_idx + 13
            compressed = all_bytes[data_start:data_start + info['data_length']]

            if info['is_encrypted']:
                if not password:
                    raise ValueError("Data is encrypted! Password required.")
                compressed = CryptoEngine.decrypt(compressed, password)

            data = zlib.decompress(compressed)

            result = {
                'type': info['data_type'],
                'encrypted': info['is_encrypted'],
                'size': len(data),
                'data': data
            }

            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(data)
                result['saved_to'] = output_path

            return result

        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
            return None

# ═══════════════════════════════════════════════════════════════
# Interactive CLI
# ═══════════════════════════════════════════════════════════════
class ShadowCLI:
    def __init__(self):
        self.running = True
        self.output_dir = "shadow_outputs"
        os.makedirs(self.output_dir, exist_ok=True)

    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_banner(self):
        self.clear()
        print(LOGO)

    def print_menu(self):
        print(f"""
{Colors.CYAN}┌─────────────────────────────────────────────────────────┐{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[1]{Colors.END} {Colors.GREEN}Hide Secret{Colors.END}    - Hide text/file inside image     {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[2]{Colors.END} {Colors.GREEN}Extract Secret{Colors.END} - Extract hidden data from image  {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[3]{Colors.END} {Colors.YELLOW}Check Capacity{Colors.END} - Check image capacity for hiding {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[4]{Colors.END} {Colors.BLUE}View Outputs{Colors.END}   - List generated files            {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[5]{Colors.END} {Colors.MAGENTA}About{Colors.END}          - Tool Information                {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[0]{Colors.END} {Colors.RED}Exit{Colors.END}           - Close the tool                  {Colors.CYAN}│{Colors.END}
{Colors.CYAN}└─────────────────────────────────────────────────────────┘{Colors.END}
        """)

    def hide_menu(self):
        print(f"\n{Colors.CYAN}[+] Hide Secret Mode{Colors.END}")
        print(f"{Colors.DARK}─────────────────────{Colors.END}")

        cover = input(f"{Colors.YELLOW}[?]{Colors.END} Cover Image Path: ").strip()
        if not os.path.exists(cover):
            print(f"{Colors.RED}[!] File not found!{Colors.END}")
            return

        print(f"\nWhat do you want to hide?")
        print(f"1. Text Message")
        print(f"2. File (Any type)")
        sub_choice = input(f"{Colors.CYAN}[>]{Colors.END} Choice: ").strip()

        if sub_choice == '1':
            secret = input(f"{Colors.YELLOW}[?]{Colors.END} Enter Secret Text: ").strip()
            data_type = 'text'
        elif sub_choice == '2':
            secret = input(f"{Colors.YELLOW}[?]{Colors.END} Secret File Path: ").strip()
            if not os.path.exists(secret):
                print(f"{Colors.RED}[!] File not found!{Colors.END}")
                return
            data_type = 'file'
        else:
            return

        out_name = input(f"{Colors.YELLOW}[?]{Colors.END} Output Name (e.g., secret.png): ").strip()
        if not out_name.endswith('.png'):
            out_name += '.png'
        
        output_path = os.path.join(self.output_dir, out_name)

        password = None
        use_pass = input(f"{Colors.YELLOW}[?]{Colors.END} Use Password? (y/n): ").strip().lower()
        if use_pass == 'y':
            password = getpass(f"{Colors.YELLOW}[?]{Colors.END} Password: ")

        print(f"\n{Colors.CYAN}[*] Hiding data...{Colors.END}")
        if SteganoEngine.hide(cover, secret, output_path, password, data_type):
            print(f"{Colors.GREEN}[✓] Success! Saved to: {output_path}{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] Failed to hide data.{Colors.END}")

    def extract_menu(self):
        print(f"\n{Colors.CYAN}[+] Extract Secret Mode{Colors.END}")
        print(f"{Colors.DARK}────────────────────────{Colors.END}")

        stego = input(f"{Colors.YELLOW}[?]{Colors.END} Stego Image Path: ").strip()
        if not os.path.exists(stego):
            print(f"{Colors.RED}[!] File not found!{Colors.END}")
            return

        password = None
        use_pass = input(f"{Colors.YELLOW}[?]{Colors.END} Is it encrypted? (y/n): ").strip().lower()
        if use_pass == 'y':
            password = getpass(f"{Colors.YELLOW}[?]{Colors.END} Password: ")

        out_name = input(f"{Colors.YELLOW}[?]{Colors.END} Save result as (e.g., data.txt): ").strip()
        output_path = os.path.join(self.output_dir, out_name) if out_name else None

        print(f"\n{Colors.CYAN}[*] Extracting data...{Colors.END}")
        result = SteganoEngine.extract(stego, output_path, password)
        
        if result:
            print(f"{Colors.GREEN}[✓] Data Extracted Successfully!{Colors.END}")
            print(f"{Colors.CYAN}[i] Type: {result['type']}{Colors.END}")
            print(f"{Colors.CYAN}[i] Size: {result['size']} bytes{Colors.END}")
            if result['type'] == 'text' and not output_path:
                print(f"\n{Colors.WHITE}Message: {result['data'].decode('utf-8')}{Colors.END}")
            elif output_path:
                print(f"{Colors.GREEN}[✓] Saved to: {output_path}{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] Failed to extract data.{Colors.END}")

    def check_capacity(self):
        print(f"\n{Colors.CYAN}[+] Capacity Check{Colors.END}")
        print(f"{Colors.DARK}───────────────────{Colors.END}")
        path = input(f"{Colors.YELLOW}[?]{Colors.END} Image Path: ").strip()
        if not os.path.exists(path):
            print(f"{Colors.RED}[!] File not found!{Colors.END}")
            return

        try:
            img = Image.open(path)
            w, h = img.size
            c = len(img.getbands())
            cap = (w * h * c) // 8 - 100 # Approx minus header
            print(f"\n{Colors.GREEN}[i] Image: {w}x{h} ({c} channels){Colors.END}")
            print(f"{Colors.GREEN}[i] Max Capacity: {cap:,} bytes ({cap/1024:.2f} KB){Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}[!] Error: {e}{Colors.END}")

    def view_outputs(self):
        print(f"\n{Colors.CYAN}[+] Generated Files (shadow_outputs/){Colors.END}")
        print(f"{Colors.DARK}───────────────────────────────────────{Colors.END}")
        files = os.listdir(self.output_dir)
        if not files:
            print(f"{Colors.YELLOW}[i] No files generated yet.{Colors.END}")
        else:
            for i, f in enumerate(files, 1):
                path = os.path.join(self.output_dir, f)
                size = os.path.getsize(path)
                print(f"  {Colors.DARK}[{i}]{Colors.END} {Colors.WHITE}{f}{Colors.END} ({size/1024:.1f} KB)")
        
    def about(self):
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
{Colors.CYAN}║{Colors.END}                    {Colors.BOLD}SHADOW v{__version__}{Colors.END}                      {Colors.CYAN}║{Colors.END}
{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.GREEN}Advanced Steganography Tool for Termux & Linux{Colors.END}      {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}                                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.YELLOW}Features:{Colors.END}                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • Hide text, files, and images inside PNG/JPG         {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • AES-256 Encryption (Optional)                       {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • zlib Compression for better capacity                {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • English Interface for better Termux compatibility   {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • Automatic Output Management (shadow_outputs/)       {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}                                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.BLUE}GitHub:{Colors.END} https://github.com/mohmmadsedeg30-design/shadow  {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.MAGENTA}Author:{Colors.END} mohmmadsedeg30-design                            {Colors.CYAN}║{Colors.END}
{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """)

    def run(self):
        self.print_banner()
        while self.running:
            self.print_menu()
            choice = input(f"{Colors.CYAN}[>]{Colors.END} Choice: ").strip()

            if choice == '1':
                self.hide_menu()
            elif choice == '2':
                self.extract_menu()
            elif choice == '3':
                self.check_capacity()
            elif choice == '4':
                self.view_outputs()
            elif choice == '5':
                self.about()
            elif choice == '0':
                print(f"\n{Colors.GREEN}[✓] Goodbye!{Colors.END}")
                self.running = False
            else:
                print(f"{Colors.RED}[!] Invalid Choice!{Colors.END}")

            if self.running:
                input(f"\n{Colors.DARK}Press Enter to continue...{Colors.END}")

# ═══════════════════════════════════════════════════════════════
# CLI Mode (Fast Usage)
# ═══════════════════════════════════════════════════════════════
def cli_mode():
    parser = argparse.ArgumentParser(
        description='Shadow - Advanced Steganography Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Examples:{Colors.END}
  {Colors.GREEN}# Interactive Mode{Colors.END}
  python shadow.py

  {Colors.GREEN}# Hide File{Colors.END}
  python shadow.py hide -c cover.png -s secret.txt -o output.png

  {Colors.GREEN}# Hide Text{Colors.END}
  python shadow.py hide -c cover.png -t "Hello World" -o output.png

  {Colors.GREEN}# Hide with Encryption{Colors.END}
  python shadow.py hide -c cover.png -s secret.zip -o output.png -p

  {Colors.GREEN}# Extract{Colors.END}
  python shadow.py extract -i output.png -o extracted.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    hide_parser = subparsers.add_parser('hide', help='Hide data in image')
    hide_parser.add_argument('-c', '--cover', required=True, help='Cover image')
    hide_parser.add_argument('-s', '--secret', help='Secret file')
    hide_parser.add_argument('-t', '--text', help='Secret text')
    hide_parser.add_argument('-o', '--output', required=True, help='Output image')
    hide_parser.add_argument('-p', '--password', action='store_true', help='Use password')

    extract_parser = subparsers.add_parser('extract', help='Extract data from image')
    extract_parser.add_argument('-i', '--input', required=True, help='Stego image')
    extract_parser.add_argument('-o', '--output', help='Output file')
    extract_parser.add_argument('-p', '--password', action='store_true', help='Encrypted data')

    check_parser = subparsers.add_parser('check', help='Check image capacity')
    check_parser.add_argument('-i', '--input', required=True, help='Image path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'hide':
        if args.text:
            password = getpass("Password: ") if args.password else None
            success = SteganoEngine.hide(args.cover, args.text, args.output, password, 'text')
        elif args.secret:
            password = getpass("Password: ") if args.password else None
            data_type = 'image' if args.secret.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else 'file'
            success = SteganoEngine.hide(args.cover, args.secret, args.output, password, data_type)
        else:
            print(f"{Colors.RED}[!] Specify -s for file or -t for text{Colors.END}")
            return

        if success:
            print(f"{Colors.GREEN}[✓] Success: {args.output}{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] Failed{Colors.END}")

    elif args.command == 'extract':
        password = getpass("Password: ") if args.password else None
        result = SteganoEngine.extract(args.input, args.output, password)
        if result:
            print(f"{Colors.GREEN}[✓] Success!{Colors.END}")
            if args.output:
                print(f"{Colors.CYAN}[i] Saved to: {args.output}{Colors.END}")
            else:
                print(f"{Colors.CYAN}[i] Type: {result['type']}, Size: {result['size']} bytes{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] Failed{Colors.END}")

    elif args.command == 'check':
        img = Image.open(args.input)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        h, w, c = pixels.shape
        capacity = (h * w * c) // 8 - 100
        print(f"{Colors.GREEN}[✓] Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB){Colors.END}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_mode()
    else:
        cli = ShadowCLI()
        cli.run()

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

__version__ = "2.0.0"
__author__ = "mohmmadsedeg30-design"

# ═══════════════════════════════════════════════════════════════
# الألوان في الطرفية (للتأثير البصري)
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
# شعار Shadow النصي (ASCII Art)
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
# أدوات التشفير (AES-256 عبر Fernet)
# ═══════════════════════════════════════════════════════════════
class CryptoEngine:
    """محرك التشفير - يحمي البيانات قبل إخفائها"""

    @staticmethod
    def _derive_key(password: str, salt: bytes = None) -> tuple:
        """اشتقاق مفتاح قوي من كلمة المرور"""
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
        """تشفير البيانات"""
        key, salt = CryptoEngine._derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(data)
        return salt + encrypted

    @staticmethod
    def decrypt(data: bytes, password: str) -> bytes:
        """فك التشفير"""
        salt = data[:16]
        encrypted = data[16:]
        key, _ = CryptoEngine._derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted)

# ═══════════════════════════════════════════════════════════════
# محرك الإخفاء (LSB - Least Significant Bit)
# ═══════════════════════════════════════════════════════════════
class SteganoEngine:
    """محرك الإخفاء بالبت الأقل أهمية (LSB)"""

    # توقيع خاص بـ Shadow للتعرف على الملفات
    SIGNATURE = b'SHADOW\x00'
    VERSION = b'\x02'

    @staticmethod
    def _bytes_to_bits(data: bytes) -> str:
        """تحويل بايتات إلى سلسلة بتات"""
        return ''.join(format(byte, '08b') for byte in data)

    @staticmethod
    def _bits_to_bytes(bits: str) -> bytes:
        """تحويل سلسلة بتات إلى بايتات"""
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    @staticmethod
    def _create_header(data_len: int, is_encrypted: bool, data_type: str) -> bytes:
        """إنشاء رأس الملف المخفي"""
        type_map = {'text': 0, 'file': 1, 'image': 2}
        type_byte = type_map.get(data_type, 1)
        flags = 0x01 if is_encrypted else 0x00

        header = struct.pack('>7sBIB', 
            SteganoEngine.SIGNATURE,  # التوقيع
            SteganoEngine.VERSION[0],  # الإصدار
            data_len,                  # حجم البيانات
            (flags << 4) | type_byte   # النوع والعلامات
        )
        return header

    @staticmethod
    def _parse_header(header: bytes) -> dict:
        """تحليل رأس الملف المخفي"""
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
        """
        إخفاء ملف/نص/صورة داخل صورة

        Args:
            cover_path: مسار الصورة الغلاف
            secret_path: مسار الملف المخفي (أو النص المباشر)
            output_path: مسار الصورة الناتجة
            password: كلمة المرور للتشفير (اختياري)
            data_type: نوع البيانات (text, file, image)
        """
        try:
            # قراءة الصورة الغلاف
            img = Image.open(cover_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)
            height, width, channels = pixels.shape
            max_capacity = height * width * channels // 8

            # قراءة البيانات السرية
            if data_type == 'text' and not os.path.exists(secret_path):
                # النص المباشر
                secret_data = secret_path.encode('utf-8')
            else:
                with open(secret_path, 'rb') as f:
                    secret_data = f.read()

            # ضغط البيانات
            compressed = zlib.compress(secret_data, level=9)

            # تشفير إذا طُلب
            is_encrypted = False
            if password:
                compressed = CryptoEngine.encrypt(compressed, password)
                is_encrypted = True

            # إنشاء الرأس + البيانات
            header = cls._create_header(len(compressed), is_encrypted, data_type)
            full_data = header + compressed

            # التحقق من السعة
            needed_bits = len(full_data) * 8
            if needed_bits > max_capacity:
                raise ValueError(
                    f"الصورة صغيرة جداً! السعة: {max_capacity} بايت، "
                    f"المطلوب: {len(full_data)} بايت"
                )

            # تحويل إلى بتات
            bits = cls._bytes_to_bits(full_data)

            # إخفاء البتات في البت الأقل أهمية
            flat_pixels = pixels.flatten()
            for i, bit in enumerate(bits):
                flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(bit)

            # إعادة تشكيل الصورة
            new_pixels = flat_pixels.reshape(height, width, channels)
            new_img = Image.fromarray(new_pixels.astype('uint8'))
            new_img.save(output_path, 'PNG')

            return True

        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
            return False

    @classmethod
    def extract(cls, stego_path: str, output_path: str = None, password: str = None) -> dict:
        """
        استخراج البيانات المخفية من صورة

        Returns:
            dict: معلومات عن البيانات المستخرجة
        """
        try:
            # قراءة الصورة
            img = Image.open(stego_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)

            # استخراج البتات من البت الأقل أهمية
            flat_pixels = pixels.flatten()
            bits = ''.join(str(pixel & 1) for pixel in flat_pixels)

            # تحويل إلى بايتات
            all_bytes = cls._bits_to_bytes(bits)

            # البحث عن التوقيع
            sig_idx = all_bytes.find(cls.SIGNATURE)
            if sig_idx == -1:
                raise ValueError("لا يوجد بيانات مخفية في هذه الصورة!")

            # قراءة الرأس
            header = all_bytes[sig_idx:sig_idx + 13]
            info = cls._parse_header(header)

            # استخراج البيانات المضغوطة
            data_start = sig_idx + 13
            compressed = all_bytes[data_start:data_start + info['data_length']]

            # فك التشفير إذا لزم الأمر
            if info['is_encrypted']:
                if not password:
                    raise ValueError("هذه البيانات مشفرة! أدخل كلمة المرور.")
                compressed = CryptoEngine.decrypt(compressed, password)

            # فك الضغط
            data = zlib.decompress(compressed)

            # حفظ أو إرجاع
            result = {
                'type': info['data_type'],
                'encrypted': info['is_encrypted'],
                'size': len(data),
                'data': data
            }

            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(data)
                result['saved_to'] = output_path

            return result

        except Exception as e:
            print(f"{Colors.RED}[ERROR] {e}{Colors.END}")
            return None

# ═══════════════════════════════════════════════════════════════
# واجهة المستخدم التفاعلية (CLI)
# ═══════════════════════════════════════════════════════════════
class ShadowCLI:
    """واجهة المستخدم التفاعلية"""

    def __init__(self):
        self.running = True

    def clear(self):
        """مسح الشاشة"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_banner(self):
        """عرض الشعار"""
        self.clear()
        print(LOGO)

    def print_menu(self):
        """عرض القائمة الرئيسية"""
        print(f"""
{Colors.CYAN}┌─────────────────────────────────────────────────────────┐{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[1]{Colors.END} {Colors.GREEN}Hide Secret{Colors.END}    - إخفاء نص/ملف/صورة داخل صورة       {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[2]{Colors.END} {Colors.GREEN}Extract Secret{Colors.END} - استخراج البيانات المخفية             {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[3]{Colors.END} {Colors.YELLOW}Check Capacity{Colors.END} - فحص سعة الصورة للإخفاء             {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[4]{Colors.END} {Colors.BLUE}Batch Hide{Colors.END}     - إخفاء عدة ملفات دفعة واحدة        {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[5]{Colors.END} {Colors.MAGENTA}About{Colors.END}          - عن الأداة                           {Colors.CYAN}│{Colors.END}
{Colors.CYAN}│{Colors.END}  {Colors.BOLD}[0]{Colors.END} {Colors.RED}Exit{Colors.END}           - خروج                                {Colors.CYAN}│{Colors.END}
{Colors.CYAN}└─────────────────────────────────────────────────────────┘{Colors.END}
        """)

    def hide_menu(self):
        """قائمة الإخفاء"""
        print(f"\n{Colors.CYAN}[+] Hide Secret Mode{Colors.END}")
        print(f"{Colors.DARK}─────────────────────{Colors.END}")

        cover = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة الغلاف: ").strip()
        if not os.path.exists(cover):
            print(f"{Colors.RED}[!] الملف غير موجود!{Colors.END}")
            return

        print(f"\n{Colors.CYAN}نوع البيانات:{Colors.END}")
        print(f"  {Colors.BOLD}[1]{Colors.END} نص طويل (سأكتبه الآن)")
        print(f"  {Colors.BOLD}[2]{Colors.END} ملف (صورة، PDF، فيديو، إلخ)")
        print(f"  {Colors.BOLD}[3]{Colors.END} صورة أخرى")

        choice = input(f"{Colors.YELLOW}[?]{Colors.END} اختر (1-3): ").strip()

        if choice == '1':
            print(f"{Colors.CYAN}[i] اكتب النص (Ctrl+D أو Enter مرتين للإنهاء):{Colors.END}")
            lines = []
            while True:
                try:
                    line = input()
                    if line == '' and lines and lines[-1] == '':
                        break
                    lines.append(line)
                except EOFError:
                    break
            text = '\n'.join(lines)
            secret_data = text
            data_type = 'text'
        elif choice == '3':
            secret = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة المخفية: ").strip()
            secret_data = secret
            data_type = 'image'
        else:
            secret = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الملف المخفى: ").strip()
            secret_data = secret
            data_type = 'file'

        output = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة الناتجة (default: shadow_output.png): ").strip()
        if not output:
            output = "shadow_output.png"

        use_pass = input(f"{Colors.YELLOW}[?]{Colors.END} هل تريد تشفير بكلمة مرور؟ (y/n): ").strip().lower()
        password = None
        if use_pass == 'y':
            password = getpass(f"{Colors.YELLOW}[?]{Colors.END} أدخل كلمة المرور: ")
            confirm = getpass(f"{Colors.YELLOW}[?]{Colors.END} تأكيد كلمة المرور: ")
            if password != confirm:
                print(f"{Colors.RED}[!] كلمات المرور غير متطابقة!{Colors.END}")
                return

        print(f"\n{Colors.CYAN}[*] جاري الإخفاء...{Colors.END}")

        if SteganoEngine.hide(cover, secret_data, output, password, data_type):
            print(f"{Colors.GREEN}\n[✓] تم الإخفاء بنجاح!{Colors.END}")
            print(f"{Colors.CYAN}[i] الصورة الناتجة: {output}{Colors.END}")

            # حساب الإحصائيات
            original_size = os.path.getsize(cover)
            new_size = os.path.getsize(output)
            print(f"{Colors.DARK}    حجم الصورة الأصلي: {original_size:,} بايت{Colors.END}")
            print(f"{Colors.DARK}    حجم الصورة الناتجة: {new_size:,} بايت{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] فشل الإخفاء!{Colors.END}")

    def extract_menu(self):
        """قائمة الاستخراج"""
        print(f"\n{Colors.CYAN}[+] Extract Secret Mode{Colors.END}")
        print(f"{Colors.DARK}────────────────────────{Colors.END}")

        stego = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة المخفية: ").strip()
        if not os.path.exists(stego):
            print(f"{Colors.RED}[!] الملف غير موجود!{Colors.END}")
            return

        use_pass = input(f"{Colors.YELLOW}[?]{Colors.END} هل البيانات مشفرة؟ (y/n): ").strip().lower()
        password = None
        if use_pass == 'y':
            password = getpass(f"{Colors.YELLOW}[?]{Colors.END} أدخل كلمة المرور: ")

        output = input(f"{Colors.YELLOW}[?]{Colors.END} مسار حفظ الملف المستخرج (اتركه فارغاً للعرض فقط): ").strip()
        if not output:
            output = None

        print(f"\n{Colors.CYAN}[*] جاري الاستخراج...{Colors.END}")

        result = SteganoEngine.extract(stego, output, password)
        if result:
            print(f"{Colors.GREEN}\n[✓] تم الاستخراج بنجاح!{Colors.END}")
            print(f"{Colors.CYAN}[i] نوع البيانات: {result['type']}{Colors.END}")
            print(f"{Colors.CYAN}[i] الحجم: {result['size']:,} بايت{Colors.END}")
            print(f"{Colors.CYAN}[i] مشفر: {'نعم' if result['encrypted'] else 'لا'}{Colors.END}")

            if output:
                print(f"{Colors.CYAN}[i] تم الحفظ في: {result['saved_to']}{Colors.END}")
            else:
                if result['type'] == 'text':
                    print(f"\n{Colors.GREEN}═══ النص المستخرج ═══{Colors.END}")
                    print(result['data'].decode('utf-8', errors='ignore'))
                    print(f"{Colors.GREEN}═════════════════════{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] فشل الاستخراج!{Colors.END}")

    def check_capacity(self):
        """فحص سعة الصورة"""
        print(f"\n{Colors.CYAN}[+] Check Capacity{Colors.END}")
        print(f"{Colors.DARK}──────────────────{Colors.END}")

        path = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة: ").strip()
        if not os.path.exists(path):
            print(f"{Colors.RED}[!] الملف غير موجود!{Colors.END}")
            return

        try:
            img = Image.open(path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)
            height, width, channels = pixels.shape

            # السعة = (العرض × الارتفاع × القنوات) / 8 - حجم الرأس
            capacity_bytes = (height * width * channels) // 8 - 100
            capacity_kb = capacity_bytes / 1024
            capacity_mb = capacity_kb / 1024

            print(f"\n{Colors.GREEN}[✓] معلومات الصورة:{Colors.END}")
            print(f"  {Colors.CYAN}الأبعاد:{Colors.END} {width} × {height}")
            print(f"  {Colors.CYAN}الوضع:{Colors.END} {img.mode}")
            print(f"  {Colors.CYAN}السعة القصوى:{Colors.END}")
            print(f"    {Colors.YELLOW}• {capacity_bytes:,} بايت{Colors.END}")
            print(f"    {Colors.YELLOW}• {capacity_kb:.2f} كيلوبايت{Colors.END}")
            print(f"    {Colors.YELLOW}• {capacity_mb:.2f} ميجابايت{Colors.END}")

            # تقدير: نص UTF-8
            print(f"\n{Colors.DARK}  ≈ يمكن إخفاء نص {capacity_bytes:,} حرف فيها{Colors.END}")

        except Exception as e:
            print(f"{Colors.RED}[!] خطأ: {e}{Colors.END}")

    def batch_hide(self):
        """إخفاء دفعة"""
        print(f"\n{Colors.CYAN}[+] Batch Hide Mode{Colors.END}")
        print(f"{Colors.DARK}───────────────────{Colors.END}")
        print(f"{Colors.YELLOW}[!] يجب أن تكون الملفات في نفس المجلد{Colors.END}")

        folder = input(f"{Colors.YELLOW}[?]{Colors.END} مسار المجلد: ").strip()
        if not os.path.isdir(folder):
            print(f"{Colors.RED}[!] المجلد غير موجود!{Colors.END}")
            return

        cover = input(f"{Colors.YELLOW}[?]{Colors.END} مسار الصورة الغلاف: ").strip()

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        print(f"\n{Colors.CYAN}[i] الملفات الم foundة: {len(files)}{Colors.END}")

        for i, f in enumerate(files, 1):
            print(f"  {Colors.DARK}[{i}] {f}{Colors.END}")

        confirm = input(f"\n{Colors.YELLOW}[?]{Colors.END} هل تريد المتابعة؟ (y/n): ").strip().lower()
        if confirm != 'y':
            return

        output_folder = os.path.join(folder, "shadow_outputs")
        os.makedirs(output_folder, exist_ok=True)

        for i, f in enumerate(files, 1):
            input_path = os.path.join(folder, f)
            output_path = os.path.join(output_folder, f"shadow_{f}.png")

            print(f"{Colors.CYAN}[{i}/{len(files)}] إخفاء {f}...{Colors.END}", end=" ")
            if SteganoEngine.hide(cover, input_path, output_path, data_type='file'):
                print(f"{Colors.GREEN}✓{Colors.END}")
            else:
                print(f"{Colors.RED}✗{Colors.END}")

        print(f"\n{Colors.GREEN}[✓] تم الانتهاء! الملفات في: {output_folder}{Colors.END}")

    def about(self):
        """معلومات عن الأداة"""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
{Colors.CYAN}║{Colors.END}                    {Colors.BOLD}SHADOW v{__version__}{Colors.END}                      {Colors.CYAN}║{Colors.END}
{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.GREEN}Steganography Tool - إخفاء البيانات في الصور{Colors.END}          {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}                                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.YELLOW}المميزات:{Colors.END}                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • إخفاء نصوص طويلة وملفات وصور داخل صور PNG/JPG       {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • تشفير AES-256 بكلمة مرور (اختياري)                  {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • ضغط zlib لزيادة السعة                               {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • واجهة تفاعلية سهلة للمبتدئين                        {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • وضع الدفعة لإخفاء عدة ملفات                         {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • فحص سعة الصورة قبل الإخفاء                          {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}                                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.YELLOW}التقنية:{Colors.END}                                               {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • LSB (Least Significant Bit) Steganography            {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • PBKDF2 Key Derivation + Fernet (AES-128-CBC)        {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  • zlib Compression                                     {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}                                                              {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.BLUE}GitHub:{Colors.END} https://github.com/mohmmadsedeg30-design/shadow  {Colors.CYAN}║{Colors.END}
{Colors.CYAN}║{Colors.END}  {Colors.MAGENTA}Author:{Colors.END} mohmmadsedeg30-design                            {Colors.CYAN}║{Colors.END}
{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """)

    def run(self):
        """تشغيل الواجهة التفاعلية"""
        self.print_banner()

        while self.running:
            self.print_menu()
            choice = input(f"{Colors.CYAN}[>]{Colors.END} اختر خياراً: ").strip()

            if choice == '1':
                self.hide_menu()
            elif choice == '2':
                self.extract_menu()
            elif choice == '3':
                self.check_capacity()
            elif choice == '4':
                self.batch_hide()
            elif choice == '5':
                self.about()
            elif choice == '0':
                print(f"\n{Colors.GREEN}[✓] مع السلامة!{Colors.END}")
                self.running = False
            else:
                print(f"{Colors.RED}[!] خيار غير صحيح!{Colors.END}")

            if self.running:
                input(f"\n{Colors.DARK}اضغط Enter للمتابعة...{Colors.END}")

# ═══════════════════════════════════════════════════════════════
# وضع سطر الأوامر (CLI Mode)
# ═══════════════════════════════════════════════════════════════
def cli_mode():
    """وضع سطر الأوامر للاستخدام السريع"""
    parser = argparse.ArgumentParser(
        description='Shadow - Advanced Steganography Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Examples:{Colors.END}
  {Colors.GREEN}# وضع تفاعلي{Colors.END}
  python shadow.py

  {Colors.GREEN}# إخفاء ملف{Colors.END}
  python shadow.py hide -c cover.png -s secret.txt -o output.png

  {Colors.GREEN}# إخفاء نص{Colors.END}
  python shadow.py hide -c cover.png -t "Hello World" -o output.png

  {Colors.GREEN}# إخفاء مع تشفير{Colors.END}
  python shadow.py hide -c cover.png -s secret.zip -o output.png -p

  {Colors.GREEN}# استخراج{Colors.END}
  python shadow.py extract -i output.png -o extracted.txt

  {Colors.GREEN}# استخراج مشفر{Colors.END}
  python shadow.py extract -i output.png -o extracted.zip -p

  {Colors.GREEN}# فحص سعة{Colors.END}
  python shadow.py check -i image.png
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # hide
    hide_parser = subparsers.add_parser('hide', help='إخفاء بيانات في صورة')
    hide_parser.add_argument('-c', '--cover', required=True, help='صورة الغلاف')
    hide_parser.add_argument('-s', '--secret', help='ملف مخفي')
    hide_parser.add_argument('-t', '--text', help='نص مخفي')
    hide_parser.add_argument('-o', '--output', required=True, help='الصورة الناتجة')
    hide_parser.add_argument('-p', '--password', action='store_true', help='استخدام كلمة مرور')

    # extract
    extract_parser = subparsers.add_parser('extract', help='استخراج بيانات من صورة')
    extract_parser.add_argument('-i', '--input', required=True, help='الصورة المخفية')
    extract_parser.add_argument('-o', '--output', help='ملف الإخراج')
    extract_parser.add_argument('-p', '--password', action='store_true', help='البيانات مشفرة')

    # check
    check_parser = subparsers.add_parser('check', help='فحص سعة الصورة')
    check_parser.add_argument('-i', '--input', required=True, help='مسار الصورة')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'hide':
        if args.text:
            password = getpass("كلمة المرور: ") if args.password else None
            success = SteganoEngine.hide(args.cover, args.text, args.output, password, 'text')
        elif args.secret:
            password = getpass("كلمة المرور: ") if args.password else None
            data_type = 'image' if args.secret.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else 'file'
            success = SteganoEngine.hide(args.cover, args.secret, args.output, password, data_type)
        else:
            print(f"{Colors.RED}[!] حدد -s للملف أو -t للنص{Colors.END}")
            return

        if success:
            print(f"{Colors.GREEN}[✓] تم الإخفاء بنجاح: {args.output}{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] فشل الإخفاء{Colors.END}")

    elif args.command == 'extract':
        password = getpass("كلمة المرور: ") if args.password else None
        result = SteganoEngine.extract(args.input, args.output, password)
        if result:
            print(f"{Colors.GREEN}[✓] تم الاستخراج بنجاح!{Colors.END}")
            if args.output:
                print(f"{Colors.CYAN}[i] حفظ في: {args.output}{Colors.END}")
            else:
                print(f"{Colors.CYAN}[i] النوع: {result['type']}, الحجم: {result['size']} بايت{Colors.END}")
        else:
            print(f"{Colors.RED}[✗] فشل الاستخراج{Colors.END}")

    elif args.command == 'check':
        img = Image.open(args.input)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        h, w, c = pixels.shape
        capacity = (h * w * c) // 8 - 100
        print(f"{Colors.GREEN}[✓] السعة: {capacity:,} بايت ({capacity/1024:.2f} KB){Colors.END}")

# ═══════════════════════════════════════════════════════════════
# نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli_mode()
    else:
        cli = ShadowCLI()
        cli.run()

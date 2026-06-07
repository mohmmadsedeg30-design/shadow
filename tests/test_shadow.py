#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Shadow Steganography Tool
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shadow import SteganoEngine, CryptoEngine

class TestShadow(unittest.TestCase):
    """اختبارات وحدة Shadow"""

    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.temp_dir = tempfile.mkdtemp()
        # إنشاء صورة تجريبية 100x100 RGB
        from PIL import Image
        import numpy as np

        img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        self.cover_path = os.path.join(self.temp_dir, "cover.png")
        img.save(self.cover_path)

        self.secret_text = "هذا نص سري للاختبار!"
        self.secret_path = os.path.join(self.temp_dir, "secret.txt")
        with open(self.secret_path, 'w', encoding='utf-8') as f:
            f.write(self.secret_text)

        self.output_path = os.path.join(self.temp_dir, "output.png")

    def test_hide_and_extract_text(self):
        """اختبار إخفاء واستخراج نص"""
        # Hide
        result = SteganoEngine.hide(
            self.cover_path, 
            self.secret_text, 
            self.output_path, 
            data_type='text'
        )
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))

        # Extract
        extracted = SteganoEngine.extract(self.output_path)
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted['type'], 'text')
        self.assertEqual(extracted['data'].decode('utf-8'), self.secret_text)

    def test_hide_and_extract_file(self):
        """اختبار إخفاء واستخراج ملف"""
        # Hide
        result = SteganoEngine.hide(
            self.cover_path,
            self.secret_path,
            self.output_path,
            data_type='file'
        )
        self.assertTrue(result)

        # Extract
        extracted = SteganoEngine.extract(self.output_path)
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted['type'], 'file')

    def test_encrypted_hide_extract(self):
        """اختبار الإخفاء المشفر"""
        password = "test_password_123"

        # Hide with encryption
        result = SteganoEngine.hide(
            self.cover_path,
            self.secret_text,
            self.output_path,
            password=password,
            data_type='text'
        )
        self.assertTrue(result)

        # Extract without password (should fail)
        extracted = SteganoEngine.extract(self.output_path)
        self.assertIsNone(extracted)

        # Extract with correct password
        extracted = SteganoEngine.extract(self.output_path, password=password)
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted['data'].decode('utf-8'), self.secret_text)

    def test_crypto_engine(self):
        """اختبار محرك التشفير"""
        data = b"test data for encryption"
        password = "my_secret_password"

        encrypted = CryptoEngine.encrypt(data, password)
        self.assertNotEqual(encrypted, data)

        decrypted = CryptoEngine.decrypt(encrypted, password)
        self.assertEqual(decrypted, data)

    def test_capacity_check(self):
        """اختبار فحص السعة"""
        from PIL import Image
        import numpy as np

        img = Image.open(self.cover_path)
        pixels = np.array(img)
        h, w, c = pixels.shape
        capacity = (h * w * c) // 8 - 100

        self.assertGreater(capacity, 0)
        # 100x100x3 = 30000 pixels = 3750 bytes capacity
        self.assertGreaterEqual(capacity, 3000)

if __name__ == '__main__':
    unittest.main()

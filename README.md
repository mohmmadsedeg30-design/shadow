<div align="center">

# 🔒 SHADOW

**Advanced Steganography Tool - Hide Secrets In Plain Sight**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Windows-orange.svg)]()

```
     ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
     ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
     ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
     ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
     ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝
              ═══ Advanced Steganography Tool ═══
```

</div>

## 🚀 المميزات (Features)

- ✅ **إخفاء نصوص طويلة** - اكتب نصاً طويلاً واخفيه داخل صورة
- ✅ **إخفاء ملفات** - PDF, ZIP, EXE, أي نوع ملف
- ✅ **إخفاء صور** - اخفِ صورة داخل صورة أخرى
- ✅ **تشفير AES-256** - حماية إضافية بكلمة مرور
- ✅ **ضغط zlib** - زيادة السعة بنسبة 70%
- ✅ **واجهة تفاعلية** - سهلة للمبتدئين (Interactive CLI)
- ✅ **وضع سطر الأوامر** - سريع للمحترفين (Command Line Mode)
- ✅ **وضع الدفعة** - إخفاء عدة ملفات دفعة واحدة
- ✅ **فحص السعة** - اعرف قدرة الصورة قبل الإخفاء

## 📦 التثبيت (Installation)

### Linux / Termux
```bash
# 1. Clone المستودع
git clone https://github.com/mohmmadsedeg30-design/shadow.git
cd shadow

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. تشغيل الأداة
python src/shadow.py
```

### Windows
```bash
git clone https://github.com/mohmmadsedeg30-design/shadow.git
cd shadow
pip install -r requirements.txt
python src/shadow.py
```

## 🎮 الاستخدام (Usage)

### الوضع التفاعلي (Interactive Mode)
```bash
python src/shadow.py
```

### وضع سطر الأوامر (CLI Mode)

**إخفاء ملف:**
```bash
python src/shadow.py hide -c cover.png -s secret.pdf -o output.png
```

**إخفاء نص:**
```bash
python src/shadow.py hide -c cover.png -t "النص السري هنا" -o output.png
```

**إخفاء مع تشفير:**
```bash
python src/shadow.py hide -c cover.png -s secret.zip -o output.png -p
```

**استخراج:**
```bash
python src/shadow.py extract -i output.png -o extracted.zip
```

**استخراج مشفر:**
```bash
python src/shadow.py extract -i output.png -o extracted.zip -p
```

**فحص سعة الصورة:**
```bash
python src/shadow.py check -i image.png
```

## 🔧 التقنية (Technical Details)

| التقنية | الوصف |
|---------|-------|
| **LSB** | Least Significant Bit - إخفاء في البت الأقل أهمية |
| **AES-256** | تشفير قوي عبر Fernet (cryptography) |
| **PBKDF2** | 480,000 iteration key derivation |
| **zlib** | ضغط بمستوى 9 (أقصى ضغط) |
| **PNG** | الصورة الناتجة دائماً PNG للحفاظ على البيانات |

## 📊 السعة (Capacity)

| أبعاد الصورة | السعة القصوى | نص UTF-8 |
|-------------|-------------|----------|
| 1920×1080 | ~780 KB | ~780,000 حرف |
| 4000×3000 | ~4.5 MB | ~4,500,000 حرف |
| 8000×6000 | ~18 MB | ~18,000,000 حرف |

## 🛡️ الأمان (Security)

- التوقيع الرقمي `SHADOW\x00` للتعرف على الملفات
- تشفير اختياري بـ AES-256 + PBKDF2
- ضغط zlib قبل الإخفاء
- لا يترك أثراً في البيانات الوصفية (Metadata)

## 📁 هيكل المشروع (Project Structure)

```
shadow/
├── src/
│   └── shadow.py          # الملف الرئيسي
├── assets/
│   └── logo.txt           # شعار ASCII
├── examples/
│   ├── sample_cover.png   # صورة تجريبية
│   └── sample_secret.txt  # نص تجريبي
├── tests/
│   └── test_shadow.py     # اختبارات
├── requirements.txt       # المتطلبات
├── README.md             # هذا الملف
├── LICENSE               # رخصة MIT
└── .gitignore           # ملفات Git
```

## 🤝 المساهمة (Contributing)

Pull requests مرحب بها! للمساهمة:
1. Fork المستودع
2. أنشئ فرعاً جديداً (`git checkout -b feature/amazing`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing`)
5. افتح Pull Request

## 📜 الترخيص (License)

MIT License - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 👨‍💻 المؤلف (Author)

**mohmmadsedeg30-design**
- GitHub: [@mohmmadsedeg30-design](https://github.com/mohmmadsedeg30-design)

---

<div align="center">

**Made with 💜 by mohmmadsedeg30-design**

```
     "الأفضل مكان لإخفاء شجرة هو في الغابة"
                              - Shadow
```

</div>

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadow-stegano",
    version="2.0.0",
    author="mohmmadsedeg30-design",
    author_email="",
    description="Advanced Steganography Tool - Hide text, files & images in images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohmmadsedeg30-design/shadow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "cryptography>=41.0.0",
    ],
    entry_points={
        "console_scripts": [
            "shadow=src.shadow:cli_mode",
        ],
    },
)

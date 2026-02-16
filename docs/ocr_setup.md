# Udyam OCR Setup

## Python Dependencies

Install the Python libraries in `requirements.txt`:

```
pip install -r requirements.txt
```

## System Dependencies

### Windows

1. Install Tesseract OCR.
2. Install Poppler (for PDF support).
3. Set environment variables so the app can find them:

```
setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
setx POPPLER_PATH "C:\Program Files\poppler-xx\Library\bin"
```

### Ubuntu/Debian

```
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

## Quick Test

```
python test_ocr.py --file path/to/udyam_certificate.pdf
```

Use `--llm` if you want the LLM fallback.

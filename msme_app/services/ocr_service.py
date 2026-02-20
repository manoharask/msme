import os
import re
import shutil
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


URN_PATTERN = r"UDYAM-[A-Z]{2}-\d{2}-\d{7}"


def _normalize_urn_text(text):
    # Fix common OCR confusions in URN segments without over-normalizing.
    if not text:
        return text

    urn_like = re.compile(
        r"UDYAM-([A-Z0-9\]\[/|\\]{2,4})-([A-Z0-9\]\[/|\\]{2,3})-([A-Z0-9\]\[/|\\]{7,9})"
    )

    state_map = {
        "0": "O",
        "1": "I",
        "2": "Z",
        "5": "S",
        "6": "G",
        "8": "B",
        "]": "J",
        "|": "J",
        "/": "J",
        "\\": "J",
    }
    numeric_map = {
        "O": "0",
        "I": "1",
        "S": "5",
        "B": "8",
        "Z": "2",
        "G": "6",
    }

    def _normalize_segment(segment, mapping):
        return "".join(mapping.get(ch, ch) for ch in segment)

    def _only_alnum(text):
        return re.sub(r"[^A-Z0-9]", "", text)

    def _only_digits(text):
        return re.sub(r"[^0-9]", "", text)

    def _fix(match):
        state = _only_alnum(_normalize_segment(match.group(1), state_map))
        district = _only_digits(_normalize_segment(match.group(2), numeric_map))
        serial = _only_digits(_normalize_segment(match.group(3), numeric_map))
        if len(state) >= 2 and len(district) >= 2 and len(serial) >= 7:
            return f"UDYAM-{state[:2]}-{district[:2]}-{serial[:7]}"
        return match.group(0)

    return urn_like.sub(_fix, text)


def _configure_tesseract():
    cmd = os.getenv("TESSERACT_CMD")
    if cmd and os.path.exists(cmd):
        pytesseract.pytesseract.tesseract_cmd = cmd
        return

    detected = shutil.which("tesseract")
    if detected:
        pytesseract.pytesseract.tesseract_cmd = detected
        return

    windows_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for candidate in windows_candidates:
        if os.path.exists(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            return

    raise pytesseract.TesseractNotFoundError(
        "Tesseract OCR not found. Install Tesseract and set TESSERACT_CMD to "
        "the full path (e.g. C:\\Program Files\\Tesseract-OCR\\tesseract.exe)."
    )


def _clean_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text).strip()
    return _normalize_urn_text(text)


def preprocess_image(image):
    if isinstance(image, Image.Image):
        image = np.array(image.convert("RGB"))
    if image is None:
        raise ValueError("Image is empty or unreadable.")

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
    return denoised


def extract_text_from_image(image_path):
    _configure_tesseract()
    img = cv2.imread(image_path)
    processed = preprocess_image(img)
    custom_config = r"--oem 3 --psm 6"
    return pytesseract.image_to_string(processed, config=custom_config)


def extract_text_from_pil_image(image):
    _configure_tesseract()
    processed = preprocess_image(image)
    custom_config = r"--oem 3 --psm 6"
    return pytesseract.image_to_string(processed, config=custom_config)


def extract_text_from_pdf(pdf_path):
    poppler_path = os.getenv("POPPLER_PATH") or None
    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    full_text = []
    for image in images:
        full_text.append(extract_text_from_pil_image(image))
    return "\n\n".join(full_text)


def _extract_line_value(text, label):
    pattern = rf"{re.escape(label)}\s*:?\s*(.+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).split("\n", 1)[0].strip()
    return value or None


def _extract_date(text, label):
    pattern = rf"{re.escape(label)}\s*:?\s*(\d{{2}}/\d{{2}}/\d{{4}})"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def parse_udyam_certificate(text):
    data = {}
    if not text:
        return data

    text = _clean_text(text)

    urn_match = re.search(URN_PATTERN, text)
    data["urn"] = urn_match.group(0) if urn_match else None

    data["business_name"] = _extract_line_value(text, "NAME OF ENTERPRISE")
    data["type"] = _extract_line_value(text, "TYPE OF ENTERPRISE")
    data["activity"] = _extract_line_value(text, "MAJOR ACTIVITY")
    data["social_category"] = _extract_line_value(
        text, "SOCIAL CATEGORY OF ENTREPRENEUR"
    )

    data["incorporation_date"] = _extract_date(
        text, "DATE OF INCORPORATION/REGISTRATION OF ENTERPRISE"
    )
    data["commencement_date"] = _extract_date(
        text, "DATE OF COMMENCEMENT OF PRODUCTION/BUSINESS"
    )
    data["registration_date"] = _extract_date(text, "DATE OF UDYAM REGISTRATION")

    mobile_match = re.search(r"\bMobile\s*:?\s*(\d{10})\b", text, re.IGNORECASE)
    # Allow accidental spaces around '@' in OCR output.
    email_match = re.search(
        r"\bEmail\s*:?\s*([\w\.-]+)\s*@\s*([\w\.-]+\.\w+)\b",
        text,
        re.IGNORECASE,
    )

    address_fields = {
        "flat": "Flat/Door/Block No.",
        "premises": "Name of Premises/Building",
        "village": "Village/Town",
        "block": "Block",
        "road": "Road/Street/Lane",
        "city": "City",
        "state": "State",
        "district": "District",
        "pin": "Pin",
    }
    address = {}
    for key, label in address_fields.items():
        value = _extract_line_value(text, label)
        if value:
            address[key] = value

    data["address"] = address or None
    data["city"] = address.get("city") if address else None
    data["state"] = address.get("state") if address else None
    data["pin"] = address.get("pin") if address else None
    data["mobile"] = mobile_match.group(1) if mobile_match else None
    data["email"] = (
        f"{email_match.group(1)}@{email_match.group(2)}" if email_match else None
    )

    unit_names = []
    units_match = re.search(
        r"NAME OF UNIT\(S\)(.*?)(OFFICIAL ADDRESS|DATE OF INCORPORATION|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if units_match:
        for line in units_match.group(1).splitlines():
            match = re.match(r"\s*\d+\s*[|]?\s*(.+)", line.strip())
            if match:
                name = match.group(1).strip()
                if name:
                    unit_names.append(name)
    data["unit_names"] = unit_names or None

    nic_codes = []
    nic_activity = None
    nic_match = re.search(
        r"NATIONAL INDUSTRY CLASSIFICATION CODE\(S\)(.*?)(DATE OF UDYAM REGISTRATION|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if nic_match:
        section = nic_match.group(1)
        nic_codes = re.findall(r"\b\d{5}\b", section)
        for line in section.splitlines():
            activity_match = re.search(r"\b(\d{5})\b\s*-\s*([^|]+)", line)
            if activity_match:
                nic_activity = activity_match.group(2).strip()
                if nic_activity:
                    break
    data["nic_5_digit_codes"] = list(dict.fromkeys(nic_codes)) or None
    data["nic_activity"] = nic_activity

    return data


def validate_udyam_number(urn):
    pattern = rf"^{URN_PATTERN}$"
    if not urn or not re.match(pattern, urn):
        return {
            "valid": False,
            "reason": "Invalid URN format. Expected: UDYAM-XX-XX-XXXXXXX",
        }
    parts = urn.split("-")
    return {
        "valid": True,
        "state_code": parts[1],
        "district_code": parts[2],
        "serial_number": parts[3],
    }


def process_udyam_certificate(file_path):
    try:
        if file_path.lower().endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_path)
        else:
            raw_text = extract_text_from_image(file_path)

        certificate_data = parse_udyam_certificate(raw_text)
        if certificate_data.get("urn"):
            certificate_data["urn_validation"] = validate_udyam_number(
                certificate_data["urn"]
            )
        certificate_data["_raw_text"] = raw_text
        return certificate_data
    except pytesseract.TesseractNotFoundError as exc:
        return {"error": str(exc), "success": False}
    except Exception as exc:
        return {"error": str(exc), "success": False}


def extract_with_llm(raw_text):
    import json
    import openai

    prompt = (
        "Extract Udyam certificate data from this OCR text:\n\n"
        f"{raw_text}\n\n"
        "Return JSON with these exact fields:\n"
        '{\n  "urn": "UDYAM-XX-XX-XXXXXXX or null",\n  "business_name": "",\n'
        '  "type": "MICRO/SMALL/MEDIUM",\n  "activity": "MANUFACTURING/SERVICES/TRADING",\n'
        '  "city": "",\n  "state": "",\n  "mobile": "",\n  "email": ""\n}'
    )

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract structured data from certificates. Return only JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model wraps the JSON
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def process_with_fallback(file_path):
    try:
        result = process_udyam_certificate(file_path)
        if result.get("error"):
            return result
        if not result.get("urn"):
            raw_text = result.get("_raw_text", "")
            result = extract_with_llm(raw_text)
            if result.get("urn"):
                result["urn_validation"] = validate_udyam_number(result["urn"])
            result["extraction_method"] = "LLM"
        else:
            result["extraction_method"] = "OCR"
        return result
    except Exception as exc:
        return {"error": str(exc), "success": False}

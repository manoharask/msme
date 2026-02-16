import argparse
import json

from msme_app.services.ocr_service import (
    process_udyam_certificate,
    process_with_fallback,
)


def main():
    parser = argparse.ArgumentParser(description="Test Udyam OCR extraction")
    parser.add_argument("--file", required=True, help="Path to certificate PDF/image")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM fallback if OCR fails",
    )
    args = parser.parse_args()

    if args.llm:
        result = process_with_fallback(args.file)
    else:
        result = process_udyam_certificate(args.file)

    print("Extracted Data:")
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()

import re

_category_cache = None


def _normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u0900-\u097F\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def _has_keyword(text, keyword):
    text = f" {_normalize(text)} "
    kw = f" {_normalize(keyword)} "
    return kw.strip() and kw in text


def _normalize_keywords(keywords):
    if not keywords:
        return []
    if isinstance(keywords, list):
        return [k for k in keywords if k]
    if isinstance(keywords, str):
        raw = keywords.strip()
        if raw.startswith("[") and raw.endswith("]"):
            # Try to parse list-like strings
            try:
                import json
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [k for k in parsed if k]
            except Exception:
                pass
        # Fallback: split comma-separated keywords
        return [k.strip() for k in raw.split(",") if k.strip()]
    return []


def _get_categories(driver):
    """Fetch all categories once and cache them for the lifetime of the process."""
    global _category_cache
    if _category_cache is None:
        with driver.session() as session:
            _category_cache = list(
                session.run(
                    """
                    MATCH (c:Category)
                    RETURN c.code AS code, c.name AS name, c.keywords AS keywords
                    ORDER BY c.code
                    """
                )
            )
    return _category_cache


def categorize_products(products, driver, business_name="", transcription=""):
    """
    Score ALL categories and return the one with the most keyword hits.
    Fixes the 'first alphabetical match wins' bug where AE001 (pump) was
    incorrectly returned for solar products before RE001 was reached.
    """
    combined = " ".join(
        [*products, business_name or "", transcription or ""]
    ).strip()
    product_text = combined

    categories = _get_categories(driver)

    best_code  = "TX001"
    best_name  = "Textiles"
    best_score = 0

    for row in categories:
        keywords = _normalize_keywords(row.get("keywords"))
        # Count how many distinct keywords match (not just boolean)
        hits = sum(1 for k in keywords if _has_keyword(product_text, k))
        if hits > best_score:
            best_score = hits
            best_code  = row["code"]
            best_name  = row["name"]

    return best_code, best_name

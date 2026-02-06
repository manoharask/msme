import re


def _normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u0900-\u097F\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def _has_keyword(text, keyword):
    text = f" {_normalize(text)} "
    kw = f" {_normalize(keyword)} "
    return kw.strip() and kw in text


def categorize_products(products, driver, business_name="", transcription=""):
    combined = " ".join(
        [*products, business_name or "", transcription or ""]
    ).strip()
    product_text = combined
    with driver.session() as session:
        categories = list(
            session.run(
                """
                MATCH (c:Category)
                RETURN c.code AS code, c.name AS name, c.keywords AS keywords
                ORDER BY c.code
                """
            )
        )
    for row in categories:
        keywords = row.get("keywords") or []
        if any(_has_keyword(product_text, k) for k in keywords):
            return row["code"], row["name"]
    return "TX001", "Textiles"

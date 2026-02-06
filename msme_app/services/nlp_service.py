import json

import openai
import difflib
import re


SYSTEM_PROMPT = """Return ONLY English JSON.
Example: "मैं चेन्नई लेदर" → {"business_name": "Chennai Leather Works", "city": "Chennai", "products": ["leather belt"], "udyam": ""}"""


def extract_entities(transcription):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f'"{transcription}" → {{"business_name": "", "city": "", "products": [], "udyam": ""}}',
            },
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content.strip())


def normalize_city(city, transcription, city_list):
    if not city_list:
        return city
    city = (city or "").strip()
    if city:
        lower_map = {c.lower(): c for c in city_list}
        if city.lower() in lower_map:
            return lower_map[city.lower()]
        match = difflib.get_close_matches(city, city_list, n=1, cutoff=0.85)
        if match:
            return match[0]
    transcription_text = (transcription or "").lower()
    for c in city_list:
        if c.lower() in transcription_text:
            return c

    def best_fuzzy_match(text):
        if not text:
            return None
        scores = [
            (difflib.SequenceMatcher(None, text.lower(), c.lower()).ratio(), c)
            for c in city_list
        ]
        scores.sort(reverse=True, key=lambda x: x[0])
        return scores[0] if scores else None

    # LLM fallback to map ambiguous city to the closest known city
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Pick the best matching city from the provided list. Return only the city name from the list, or empty string if none fit.",
                },
                {
                    "role": "user",
                    "content": f"City list: {city_list}\nExtracted city: {city}\nTranscription: {transcription}",
                },
            ],
            temperature=0,
        )
        candidate = response.choices[0].message.content.strip().splitlines()[0].strip()
        if candidate:
            lower_map = {c.lower(): c for c in city_list}
            if candidate.lower() in lower_map:
                return lower_map[candidate.lower()]
    except Exception:
        pass
    best = best_fuzzy_match(city)
    if best and best[0] >= 0.8:
        return best[1]

    tokens = re.findall(r"[a-zA-Z]+", transcription_text)
    for token in tokens:
        best_token = best_fuzzy_match(token)
        if best_token and best_token[0] >= 0.8:
            return best_token[1]
    return city

"""
GraphRAG Service — Natural Language → Cypher → Neo4j → Grounded Answer
Zero hallucination: every answer is derived exclusively from live DB results.
"""
import os
import re

import openai
from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Return a cached OpenAI client using the key set by load_config() or the env var."""
    global _client
    if _client is None:
        api_key = openai.api_key or os.getenv("OPENAI_API_KEY")
        _client = OpenAI(api_key=api_key)
    return _client

# ── Graph schema description fed to the LLM ─────────────────────────────────
_SCHEMA = """
NODE: MSE (Micro/Small Enterprise)
  id, name, city, products (list), urn, mobile, email,
  type (enterprise type e.g. Proprietorship), activity, social_category,
  state, pin, unit_names (list), nic_5_digit_codes (list), nic_activity, source

NODE: SNP (Seller Network Participant — ONDC-registered service provider)
  id, name, city,
  rating (Float 0.0–1.0; 0.92 = 92%), capacity (Integer monthly units),
  export_capable (Boolean), certifications (list e.g. ["ISO9001","BIS"]),
  languages (list of codes e.g. ["en","hi","ta"]),
  payment_terms (e.g. "Net 30"), specialization, lat, lon

NODE: Category (ONDC product/service taxonomy)
  code (e.g. "TX001"), name (e.g. "Textiles & Fabrics"),
  sector (e.g. "Manufacturing"), keywords (list, includes Hindi terms),
  ondc_l1, ondc_l2, ondc_l3

RELATIONSHIPS:
  (MSE)-[:OFFERS]->(Category)  — MSE's products belong to this category
  (SNP)-[:SERVES]->(Category)  — SNP can serve MSEs in this category
"""

_CYPHER_SYSTEM = f"""You are a Neo4j Cypher expert for Udyam Mitra, an AI platform that \
connects Indian MSEs with SNPs on the ONDC network.

{_SCHEMA}

Rules (follow strictly):
1. Output ONLY a valid Cypher query — no markdown fences, no explanation, no comments.
2. Use toLower() for all string comparisons.
3. Use OPTIONAL MATCH when joining nodes that may not exist.
4. Limit results to 25 rows unless the user specifies otherwise.
5. Multiply rating by 100 when displaying as a percentage.
6. For "best" or "top" SNPs, ORDER BY s.rating DESC.
7. For matching MSEs to SNPs, traverse MSE→Category←SNP via OFFERS/SERVES.
8. When counting, use count(DISTINCT ...) to avoid duplicates.
9. NEVER search only on MSE.activity for product/sector/industry queries. Instead search
   through the Category graph: MATCH (m:MSE)-[:OFFERS]->(c:Category) and match on
   toLower(c.name), toLower(c.sector), or ANY(k IN c.keywords WHERE toLower(k) CONTAINS '...')
   Also OR-in a broad fallback across m.products list:
   ANY(p IN m.products WHERE toLower(p) CONTAINS '...') and toLower(m.nic_activity) CONTAINS '...'
   This ensures graph-semantic matching rather than plain string matching on a single field.
10. For any query about MSEs in a specific industry/sector/product type, use this pattern:
    MATCH (m:MSE)-[:OFFERS]->(c:Category)
    WHERE toLower(c.name) CONTAINS '<term>'
       OR toLower(c.sector) CONTAINS '<term>'
       OR ANY(k IN c.keywords WHERE toLower(k) CONTAINS '<term>')
       OR ANY(p IN m.products WHERE toLower(p) CONTAINS '<term>')
       OR toLower(m.nic_activity) CONTAINS '<term>'
    RETURN DISTINCT m LIMIT 25
11. For any query asking for SNPs in a specific industry/sector/category (e.g. "best SNP for
    agriculture", "recommend SNPs for textiles", "which SNPs serve food sector"):
    ALWAYS start from the SNP node — NEVER from MSE. Use this pattern:
    MATCH (s:SNP)-[:SERVES]->(c:Category)
    WHERE toLower(c.name) CONTAINS '<term>'
       OR toLower(c.sector) CONTAINS '<term>'
       OR ANY(k IN c.keywords WHERE toLower(k) CONTAINS '<term>')
    WITH DISTINCT s ORDER BY s.rating DESC LIMIT 25
    RETURN s.id, s.name, s.city,
           round(s.rating * 100) AS rating_pct,
           s.export_capable, s.certifications, s.payment_terms, s.specialization
    Do NOT use OPTIONAL MATCH for SNPs when the question is about finding SNPs —
    that produces null rows. Use a direct MATCH from SNP.
12. For ALL queries that return SNP or MSE properties (not full nodes), NEVER use
    RETURN DISTINCT with ORDER BY on the node variable — this causes a syntax error.
    Instead, always sort and deduplicate in a WITH clause BEFORE the RETURN:
      WITH DISTINCT s ORDER BY s.rating DESC LIMIT N
      RETURN s.id, s.name, ...
    For general top-N SNP queries with no category filter:
      MATCH (s:SNP)
      WITH s ORDER BY s.rating DESC LIMIT N
      RETURN s.id, s.name, s.city,
             round(s.rating * 100) AS rating_pct,
             s.export_capable, s.certifications, s.payment_terms, s.specialization
"""

_ANSWER_SYSTEM = """You are a helpful, conversational assistant for Udyam Mitra — an AI platform
that connects Indian Micro & Small Enterprises (MSEs) with ONDC Seller Network Participants (SNPs).

Given a user question and the raw database query results, write a clear, well-formatted markdown answer.

Rules (follow strictly):
1. Answer ONLY from the provided data — never invent or assume anything.
2. If results are empty, respond warmly: acknowledge what the user was looking for, let them know
   nothing matched, and suggest they try a broader term, a related category, or a different city.
   Never use technical or database language in this message.
3. Display ratings as percentages (0.92 → 92%).
4. Never mention Cypher, Neo4j, queries, databases, or any technical terms — speak naturally.
5. Keep the tone friendly, helpful, and professional.
6. Refer to SNPs as "Seller Network Participants (SNPs)" on first mention, then just "SNPs".

Formatting rules:
- Start with a one-line direct answer that summarises the finding.
- For lists of MSEs: bullet points — **Name** | City | Products: ...
- For lists of SNPs: bullet points — **Name** | City | Rating: X% | Export-Ready: Yes/No
- For counts or single values: state the number prominently, then add a brief insight.
- Bold all entity names (MSE names, SNP names, category names).
- Pick the 3–4 most relevant fields per record; omit nulls and empty lists.
- If more than 10 items, show the first 10 and note how many more exist.
"""


def _clean_cypher(text: str) -> str:
    """Strip markdown code fences the LLM may add despite instructions."""
    text = text.strip()
    # Remove ```cypher ... ``` or ``` ... ```
    text = re.sub(r"^```(?:cypher)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_cypher(question: str) -> str:
    """Convert a natural language question into a Neo4j Cypher query."""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _CYPHER_SYSTEM},
            {"role": "user", "content": f"Question: {question}"},
        ],
        temperature=0,
        max_tokens=600,
    )
    return _clean_cypher(response.choices[0].message.content)


def fix_cypher(cypher: str, error: str, question: str) -> str:
    """Ask the LLM to self-correct a failed Cypher query."""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _CYPHER_SYSTEM},
            {"role": "user", "content": f"Question: {question}"},
            {"role": "assistant", "content": cypher},
            {
                "role": "user",
                "content": (
                    f"The query failed with this error:\n{error}\n\n"
                    "Fix the Cypher query. Output ONLY the corrected query."
                ),
            },
        ],
        temperature=0,
        max_tokens=600,
    )
    return _clean_cypher(response.choices[0].message.content)


def execute_cypher(driver, cypher: str) -> list:
    """Run a Cypher query and return results as a list of dicts."""
    with driver.session() as session:
        result = session.run(cypher)
        return [dict(record) for record in result]


def format_answer(question: str, results: list) -> str:
    """Turn raw DB results into a grounded natural-language answer."""
    results_text = str(results[:25]) if results else "[]"
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _ANSWER_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Database results:\n{results_text}\n\n"
                    "Provide a helpful, factual answer based strictly on these results."
                ),
            },
        ],
        temperature=0.1,
        max_tokens=700,
    )
    return response.choices[0].message.content.strip()


def ask(driver, question: str) -> dict:
    """
    Full GraphRAG pipeline with one self-correction attempt:
      1. NL  → Cypher   (GPT-4o-mini, temp=0)
      2. Cypher → Neo4j execution
      2b. On failure: fix Cypher and retry once
      3. Results → grounded natural-language answer (GPT-4o-mini, temp=0.1)

    Returns dict with keys: answer, cypher, results, error
    """
    cypher = None
    try:
        cypher = generate_cypher(question)

        try:
            results = execute_cypher(driver, cypher)
        except Exception as exec_err:
            # Self-correction: ask LLM to fix the broken query
            fixed = fix_cypher(cypher, str(exec_err), question)
            cypher = fixed
            results = execute_cypher(driver, cypher)  # propagate if still fails

        answer = format_answer(question, results)
        return {"answer": answer, "cypher": cypher, "results": results, "error": None}

    except Exception as e:
        return {
            "answer": (
                "I'm sorry, I wasn't able to find an answer for that. "
                "Could you try rephrasing your question? You can ask me about registered enterprises, "
                "service providers, product categories, cities, ratings, or export readiness."
            ),
            "cypher": cypher,
            "results": [],
            "error": str(e),
        }

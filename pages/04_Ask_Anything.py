import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.graphrag_service import ask
from msme_app.ui import (
    apply_styles,
    configure_page,
    render_header,
    render_sidebar,
)

configure_page()


@st.cache_resource
def _get_driver():
    return get_driver(load_config())


driver = _get_driver()

apply_styles()
render_header()
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)
render_sidebar(current_page="ask_anything")

# ── Page styles ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Push content up so the sticky chat input never overlaps the last message */
.main .block-container { padding-bottom: 6rem !important; }

.aq-header {
  font-size:0.95rem;font-weight:700;color:#0b1221;
  letter-spacing:-0.01em;margin:0.1rem 0 0.1rem 0;
}
.aq-pill {
  display:inline-flex;align-items:center;gap:5px;
  background:#f0f7ff;border:1px solid #bfdbfe;border-radius:20px;
  padding:3px 10px;font-size:0.68rem;font-weight:600;color:#1d4ed8;
  margin:0 4px 6px 0;
}
.cypher-box {
  background:#0f172a;border-radius:8px;padding:0.75rem 1rem;
  font-family:'Fira Code',monospace;font-size:0.74rem;
  color:#7dd3fc;line-height:1.6;white-space:pre-wrap;overflow-x:auto;
}
/* Style the sticky chat input bar */
[data-testid="stChatInput"] {
  border-top: 2px solid #bfdbfe !important;
  background: linear-gradient(135deg,#f0f7ff 0%,#ffffff 100%) !important;
  padding: 0.6rem 1rem !important;
  box-shadow: 0 -4px 16px rgba(37,99,235,0.08) !important;
}
[data-testid="stChatInput"] textarea {
  border-radius: 12px !important;
  border: 1.5px solid #93c5fd !important;
  font-size: 0.88rem !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
hdr_col, clr_col = st.columns([5, 1])
with hdr_col:
    st.markdown(
        '<div class="aq-header">💬 Ask Anything</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Ask questions in natural language. Answers are drawn directly from the "
        "Neo4j database — no guesswork, no hallucination."
    )
with clr_col:
    if st.button("🗑 Clear", use_container_width=True):
        st.session_state.pop("aq_messages", None)
        st.rerun()

# Sample prompts
st.markdown(
    '<div style="margin:0.3rem 0 0.6rem;">'
    '<span class="aq-pill">💡 How many MSEs are registered?</span>'
    '<span class="aq-pill">💡 Which SNPs are export-ready?</span>'
    '<span class="aq-pill">💡 Top 5 SNPs by rating?</span>'
    '<span class="aq-pill">💡 SNPs in Bengaluru?</span>'
    '<span class="aq-pill">💡 MSEs in food processing?</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()

# ── Chat history initialisation ───────────────────────────────────────────────
if "aq_messages" not in st.session_state:
    st.session_state["aq_messages"] = [
        {
            "role": "assistant",
            "content": (
                "Hello! I can answer questions about the MSEs, Seller Network Participants (SNPs), "
                "and categories in your Udyam Mitra network.\n\n"
                "Every answer I give comes directly from the Neo4j graph database — "
                "no assumptions, no hallucination. Try a sample question above or type your own below."
            ),
            "cypher": None,
            "results": None,
            "error": None,
        }
    ]

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state["aq_messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🎯"):
            st.markdown(msg["content"])
            if msg.get("error"):
                with st.expander("⚠️ Debug info", expanded=False):
                    st.code(msg["error"], language="text")
                    if msg.get("cypher"):
                        st.code(msg["cypher"], language="cypher")
            elif msg.get("cypher"):
                cols = st.columns([1, 1])
                with cols[0]:
                    with st.expander("🔍 View Cypher Query", expanded=False):
                        st.markdown(
                            f'<div class="cypher-box">{msg["cypher"]}</div>',
                            unsafe_allow_html=True,
                        )
                results = msg.get("results") or []
                if results:
                    with cols[1]:
                        with st.expander(
                            f"📊 Raw Data ({len(results)} record{'s' if len(results) != 1 else ''})",
                            expanded=False,
                        ):
                            st.json(results[:10])

# ── Process question ──────────────────────────────────────────────────────────
def _process_question(question: str):
    st.session_state["aq_messages"].append(
        {"role": "user", "content": question, "cypher": None, "results": None, "error": None}
    )
    with st.spinner("Querying the database…"):
        result = ask(driver, question)
    st.session_state["aq_messages"].append(
        {
            "role": "assistant",
            "content": result["answer"],
            "cypher": result["cypher"],
            "results": result["results"],
            "error": result["error"],
        }
    )


# ── Text chat input ────────────────────────────────────────────────────────────
if typed_q := st.chat_input("Type your question here — e.g. 'Best SNPs for textiles in Mumbai'"):
    _process_question(typed_q)
    st.rerun()

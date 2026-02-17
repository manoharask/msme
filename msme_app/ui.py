import streamlit as st


def configure_page():
    st.set_page_config(layout="wide", page_title="Dashboard", page_icon="🧠")


def apply_styles():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {
  --ink: #0b1221;
  --muted: #5b6477;
  --brand: #1d4ed8;
  --brand-2: #2563eb;
  --accent: #f97316;
  --surface: #ffffff;
  --surface-2: #f7f9fc;
  --line: #e2e8f0;
}
body, .main {font-family: 'Space Grotesk', sans-serif; background: #e6edf5;}
.stApp {color: #0b1221;}
.app-shell {max-width: 1200px; margin: 0 auto;}
.header-1 {font-size: 2rem; font-weight: 700; color: var(--ink); text-align: center; margin-bottom: 0.25rem;}
.header-2 {font-size: 0.95rem; color: var(--muted); text-align: center; margin-top: 0;}
.section-title {font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0 0 0.3rem 0;}
.section-subtitle {color: var(--muted); margin: 0 0 1rem 0;}
.graph-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #2563eb 100%);
  color: #f8fafc;
  padding: 1.3rem 1.6rem;
  border-radius: 18px;
  text-align: center;
  margin-bottom: 1rem;
  box-shadow: 0 18px 40px rgba(30,64,175,0.25);
}
.graph-hero--compact {padding: 1.1rem 1.4rem;}
.metric-container {
  background: var(--surface);
  color: var(--ink);
  padding: 0.9rem 1.1rem;
  border-radius: 14px;
  height: 90px;
  border: 1px solid var(--line);
  box-shadow: 0 10px 24px rgba(2,6,23,0.08);
  position: relative;
  overflow: hidden;
}
.metric-container:after {
  content: "";
  position: absolute;
  right: -30px;
  top: -30px;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(37,99,235,0.2), transparent 60%);
}
.metric-container .label {color: var(--muted); font-size: 0.85rem;}
/* ── SNP Match Cards — compact sleek design ─────────────────── */
.snp-card-1 {
  background: linear-gradient(160deg, #0c4a6e 0%, #0369a1 100%);
  border-radius: 16px; padding: 1.25rem 1.4rem;
  box-shadow: 0 8px 24px rgba(3,105,161,0.30);
  color: #f0f9ff !important;
}
.snp-card-2 {
  background: linear-gradient(160deg, #134e4a 0%, #0f766e 100%);
  border-radius: 16px; padding: 1.25rem 1.4rem;
  box-shadow: 0 8px 24px rgba(15,118,110,0.30);
  color: #f0fdfa !important;
}
.snp-card-3 {
  background: linear-gradient(160deg, #3b0764 0%, #6d28d9 100%);
  border-radius: 16px; padding: 1.25rem 1.4rem;
  box-shadow: 0 8px 24px rgba(109,40,217,0.30);
  color: #faf5ff !important;
}
/* Score pill */
.snp-score {
  display:inline-block; font-size:1.6rem; font-weight:800;
  letter-spacing:-0.02em; line-height:1;
}
.snp-score-label {
  font-size:0.68rem; font-weight:600; letter-spacing:0.08em;
  text-transform:uppercase; opacity:0.7; display:block; margin-top:2px;
}
/* Compact info grid */
.snp-grid {
  display:grid; grid-template-columns:1fr 1fr;
  gap:0.35rem 0.6rem; margin-top:0.85rem;
}
.snp-row {
  display:flex; flex-direction:column;
  background:rgba(255,255,255,0.10);
  border-radius:8px; padding:0.35rem 0.6rem;
}
.snp-row.full { grid-column: span 2; }
.snp-lbl {
  font-size:0.62rem; font-weight:600; letter-spacing:0.07em;
  text-transform:uppercase; opacity:0.65; line-height:1.2;
}
.snp-val {
  font-size:0.82rem; font-weight:500; line-height:1.3; margin-top:1px;
}
/* Badge */
.snp-badge {
  display:inline-block; margin-top:0.75rem;
  background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.28);
  border-radius:20px; padding:0.22rem 0.75rem;
  font-size:0.68rem; font-weight:700; letter-spacing:0.06em;
  text-transform:uppercase;
}
/* Deprecate old .reasoning-card so no remnants cause layout issues */
.reasoning-card {display:none;}
/* ════════════════════════════════════════════════════════════
   FORM v4 — zero-wrapper, pure Streamlit DOM targeting
   All sizing driven by CSS vars for perfect consistency.
   ════════════════════════════════════════════════════════════ */
:root {
  --fi-h:       40px;
  --fi-fs:      0.875rem;
  --fi-radius:  9px;
  --fi-pad:     0 12px;
  --fi-bg:      #f1f5f9;
  --fi-bg-focus:#ffffff;
  --fi-border:  #dde3ec;
  --fi-hover:   #94a3b8;
  --fi-focus:   #2563eb;
  --lbl-fs:     0.72rem;
  --lbl-color:  #64748b;
  --lbl-weight: 600;
}

/* Shell */
.onboarding-card { background:transparent; border:none; box-shadow:none; padding:0; }

/* Kill Streamlit's default element gaps */
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] { gap:0 !important; }
div[data-testid="stHorizontalBlock"] { gap: 16px !important; align-items: flex-end !important; }

/* ── Text inputs ─────────────────────────────────────────── */
div[data-testid="stTextInput"] input {
  height:         var(--fi-h)      !important;
  font-size:      var(--fi-fs)     !important;
  border-radius:  var(--fi-radius) !important;
  padding:        var(--fi-pad)    !important;
  background:     var(--fi-bg)     !important;
  border:         1.5px solid var(--fi-border) !important;
  color:          #0f172a          !important;
  box-shadow:     none             !important;
  line-height:    var(--fi-h)      !important;
  transition:     border-color .15s, box-shadow .15s, background .15s !important;
  width:          100%             !important;
  box-sizing:     border-box       !important;
}
div[data-testid="stTextInput"] input:hover {
  border-color: var(--fi-hover) !important;
}
div[data-testid="stTextInput"] input:focus {
  background:   var(--fi-bg-focus) !important;
  border-color: var(--fi-focus)    !important;
  box-shadow:   0 0 0 3px rgba(37,99,235,0.13) !important;
  outline:      none !important;
}

/* ── Selectbox ───────────────────────────────────────────── */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  height:         var(--fi-h)      !important;
  min-height:     var(--fi-h)      !important;
  font-size:      var(--fi-fs)     !important;
  border-radius:  var(--fi-radius) !important;
  background:     var(--fi-bg)     !important;
  border:         1.5px solid var(--fi-border) !important;
  color:          #0f172a          !important;
  box-shadow:     none             !important;
  padding:        0 8px            !important;
  align-items:    center           !important;
  transition:     border-color .15s !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
  border-color: var(--fi-hover) !important;
}
div[data-testid="stSelectbox"] svg { color: #94a3b8 !important; }
/* Dropdown value text */
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
div[data-baseweb="select"] span { font-size: var(--fi-fs) !important; }

/* ── Labels ─────────────────────────────────────────────── */
div[data-testid="stTextInput"]  > label,
div[data-testid="stSelectbox"]  > label,
div[data-testid="stTextArea"]   > label {
  font-size:      var(--lbl-fs)     !important;
  font-weight:    var(--lbl-weight) !important;
  color:          var(--lbl-color)  !important;
  letter-spacing: 0.05em            !important;
  text-transform: uppercase         !important;
  margin-bottom:  4px               !important;
  line-height:    1.2               !important;
}

/* ── Section pill — self-contained, no open div ─────────── */
.fsec {
  display:        inline-flex;
  align-items:    center;
  gap:            6px;
  padding:        4px 12px 4px 8px;
  border-radius:  100px;
  font-size:      0.68rem;
  font-weight:    700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  margin:         18px 0 8px 0;
  border:         1.5px solid currentColor;
}
.fsec-icon  { font-size: 0.8rem; line-height:1; }
.fsec-blue  { color:#1d4ed8; background:#eff6ff; }
.fsec-green { color:#15803d; background:#f0fdf4; }
.fsec-violet{ color:#6d28d9; background:#f5f3ff; }
.fsec-amber { color:#92400e; background:#fffbeb; }
.fsec-rose  { color:#9f1239; background:#fff1f2; }

/* Divider line below each section's last field row */
.fsec + div { border-top: none !important; }

/* ── Save button ─────────────────────────────────────────── */
div[data-testid="stButton"] > button {
  height:         44px !important;
  padding:        0 32px !important;
  background:     linear-gradient(135deg,#1e40af,#2563eb) !important;
  color:          #fff !important;
  border:         none !important;
  border-radius:  10px !important;
  font-size:      var(--fi-fs) !important;
  font-weight:    700 !important;
  letter-spacing: 0.02em !important;
  box-shadow:     0 4px 14px rgba(37,99,235,.38) !important;
  transition:     transform .12s, box-shadow .12s, filter .12s !important;
  cursor:         pointer !important;
}
div[data-testid="stButton"] > button:hover {
  transform:  translateY(-2px) !important;
  box-shadow: 0 8px 22px rgba(37,99,235,.45) !important;
  filter:     brightness(1.07) !important;
}
div[data-testid="stButton"] > button:active { transform:none !important; }

.onboarding-step {
  background:var(--surface-2); border:1px solid var(--line);
  padding:.75rem 1rem; border-radius:12px;
  margin-bottom:.75rem; color:var(--ink);
}
.match-header {display: block; width: 100%; padding: 0.25rem 0 0.75rem 0; border-bottom: 1px solid var(--line); margin: 0 0 0.75rem 0; text-align: left; padding-left: 0;}
.match-header .section-title, .match-header .section-subtitle {text-align: left; margin-left: 0;}
/* Tighten onboarding spacing */
section[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stTabs"]) {margin-top: 0.2rem;}
div[data-testid="stTabs"] {margin-top: 0.25rem; margin-bottom: 0.5rem;}
.stTabs [data-baseweb="tab-panel"] > div:empty {display:none;}
.stTabs [data-baseweb="tab-panel"] > div:has(> div:empty) {display:none;}
.stFileUploader {margin-top: 0.35rem;}
.stFileUploader section {padding: 0.5rem 0.75rem !important;}
.stFileUploader button {background: #1d4ed8 !important; color: #fff !important; border: none !important;}
.stFileUploader button:hover {filter: brightness(1.05);}
.stFileUploader small {color: #64748b !important;}
.onboarding-header {max-width: 1200px; margin: 0 auto 0.35rem auto; text-align: left;}
.onboarding-header .section-title {font-size: 1.2rem; margin: 0; text-align: left !important;}
.onboarding-header .section-subtitle {margin: 0.1rem 0 0.4rem 0; text-align: left !important;}
.onboarding-block {margin-left: 0; padding-left: 0;}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
<div class="app-shell">
    <div class="header-1">🧠 MSME TEAM GraphRAG Platform</div>
    <div class="header-2">Neo4j Knowledge Graph Reasoning | IndiaAI Innovation Challenge 2026</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
<div class="app-shell">
    <div class="graph-hero graph-hero--compact">
        <h3 style='margin-bottom: 0.4rem; color: #ffffff;'>Multi-hop Graph Reasoning: MSE → Category → SNP + Network Effects</h3>
        <p style='font-size: 0.98rem; opacity: 0.9; margin: 0; color: #ffffff;'>Voice → AI → ONDC Taxonomy → Intelligent Matching</p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_metrics():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-container"><div style="font-size:2.2rem;font-weight:700;">7.6Cr</div><div class="label">MSMEs</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-container"><div style="font-size:2.2rem;font-weight:700;">4.55Cr</div><div class="label">Udyam Registered</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-container"><div style="font-size:2.2rem;font-weight:700;">1.59Cr</div><div class="label">Manufacturing</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            '<div class="metric-container"><div style="font-size:2.2rem;font-weight:700;">94%</div><div class="label">Graph Accuracy</div></div>',
            unsafe_allow_html=True,
        )


def render_graph_header():
    st.markdown(
        """
<div class="match-header">
  <div class="section-title">Intelligent SNP Matching</div>
  <div class="section-subtitle">Top SNPs ranked with clear evidence and scoring factors.</div>
</div>
""",
        unsafe_allow_html=True,
    )
def render_reasoning_cards(reasoning_result, mse_city, category_name, category_code):
    if not reasoning_result:
        st.warning(
            f"\u26a0\ufe0f No SNP matches found for **{category_name} ({category_code})** "
            f"in or near **{mse_city}**.\n\n"
            "**Possible reasons:**\n"
            "- No SNP in the graph serves this category yet\n"
            "- City name doesn't match any SNP city\n"
            "- No SNP has rating > 0.85 (the fallback threshold)\n\n"
            "Run `seed_graph.py` to ensure SNPs are populated."
        )
        return

    num_results = len(reasoning_result)
    cols = st.columns(min(num_results, 3))

    card_styles = ["snp-card-1", "snp-card-2", "snp-card-3"]
    medals      = ["\U0001f947", "\U0001f948", "\U0001f949"]
    labels      = ["TOP MATCH", "STRONG MATCH", "GOOD MATCH"]

    for i, result in enumerate(reasoning_result):
        with cols[i]:
            city_match  = str(result["location"]).strip().lower() == str(mse_city).strip().lower()
            geo_icon    = "&#128205;" if city_match else "&#127758;"
            geo_label   = result["location"]

            certs        = result.get("certifications") or []
            cert_text    = ", ".join(certs) if certs else "None"
            cert_count   = result.get("cert_count") or len(certs)

            export_capable = result.get("export_capable", False)
            export_text    = "Yes &#9989;" if export_capable else "No"
            sla_note       = " +5%" if export_capable else ""

            specialization = (result.get("specialization") or "")[:42]
            spec_row = (
                f'<div class="snp-row full">'
                f'<span class="snp-lbl">&#128161; Specialization</span>'
                f'<span class="snp-val">{specialization}</span></div>'
            ) if specialization else ""

            payment  = result.get("payment_terms") or "N/A"
            badge    = labels[i] if i < len(labels) else ""
            medal    = medals[i] if i < len(medals) else ""

            st.markdown(f"""
<div class="{card_styles[i]}">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:0.5rem;">
    <div>
      <div style="font-size:0.78rem;opacity:0.7;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:2px;">{medal} {result['snp']}</div>
      <div class="snp-score">{result['score']}%</div>
      <span class="snp-score-label">Match Score</span>
    </div>
    <div style="text-align:right;">
      <div class="snp-badge">{badge}</div>
      <div style="font-size:0.72rem;opacity:0.65;margin-top:0.4rem;">{geo_icon} {geo_label}</div>
    </div>
  </div>
  <div class="snp-grid">
    <div class="snp-row">
      <span class="snp-lbl">&#128200; Geo</span>
      <span class="snp-val">{result['geo_pct']}%</span>
    </div>
    <div class="snp-row">
      <span class="snp-lbl">&#11088; SLA{sla_note}</span>
      <span class="snp-val">{result['sla_pct']}%</span>
    </div>
    <div class="snp-row">
      <span class="snp-lbl">&#128230; Capacity</span>
      <span class="snp-val">{result['cap_pct']}%</span>
    </div>
    <div class="snp-row">
      <span class="snp-lbl">&#127760; Export</span>
      <span class="snp-val">{export_text}</span>
    </div>
    <div class="snp-row">
      <span class="snp-lbl">&#127885; Certs ({cert_count})</span>
      <span class="snp-val">{cert_text}</span>
    </div>
    <div class="snp-row">
      <span class="snp-lbl">&#128179; Payment</span>
      <span class="snp-val">{payment}</span>
    </div>
    {spec_row}
  </div>
</div>
""", unsafe_allow_html=True)


def render_dashboard_header():
    st.markdown("---")
    st.header("📊 Graph-Powered Business Intelligence")



def render_footer():
    st.markdown(
        """
<div style='text-align:center;padding:2rem;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);border-radius:20px;margin-top:2rem;'>
    <h3 style='color:#1e40af;'>AI&S India LLP | IndiaAI Innovation Challenge 2026</h3>
    <p><strong>Problem Statement 2:</strong> AI-powered MSE Agent mapping tool | Neo4j GraphRAG</p>
</div>
""",
        unsafe_allow_html=True,
    )

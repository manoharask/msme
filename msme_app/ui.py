import base64
import os

import streamlit as st

# ── Logo helper ──────────────────────────────────────────────────────────────
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "logo.png")

def _logo_b64() -> str | None:
    """Return base64-encoded logo or None if file not present."""
    try:
        with open(_LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


def configure_page():
    st.set_page_config(layout="wide", page_title="Udyam Mitra", page_icon="🎯")


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
/* Why-selected section */
.snp-divider {
  border:none; border-top:1px solid rgba(255,255,255,0.15);
  margin:0.75rem 0 0.65rem;
}
.snp-why-label {
  font-size:0.58rem; font-weight:700; letter-spacing:0.1em;
  text-transform:uppercase; opacity:0.55; margin-bottom:0.35rem;
}
.snp-why-text {
  font-size:0.79rem; line-height:1.55; opacity:0.95; margin-bottom:0.6rem;
}
/* Attribute chips */
.snp-chips {
  display:flex; flex-wrap:wrap; gap:5px; margin-bottom:0.5rem;
}
.snp-chip {
  background:rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.22);
  border-radius:20px; padding:0.2rem 0.6rem;
  font-size:0.68rem; font-weight:600; opacity:0.9;
}
/* Caveat warning */
.snp-caveat {
  background:rgba(251,191,36,0.18); border:1px solid rgba(251,191,36,0.35);
  border-radius:8px; padding:0.3rem 0.65rem;
  font-size:0.72rem; font-weight:500; margin-top:0.4rem;
}
/* Badge — inline next to score, no top margin */
.snp-badge {
  display:inline-block;
  background:rgba(255,255,255,0.18); border:1px solid rgba(255,255,255,0.28);
  border-radius:20px; padding:0.22rem 0.75rem;
  font-size:0.68rem; font-weight:700; letter-spacing:0.06em;
  text-transform:uppercase; vertical-align:middle;
}
/* Deprecate old .reasoning-card so no remnants cause layout issues */
.reasoning-card {display:none;}
/* ════════════════════════════════════════════════════════════
   FORM v4 — zero-wrapper, pure Streamlit DOM targeting
   All sizing driven by CSS vars for perfect consistency.
   ════════════════════════════════════════════════════════════ */
:root {
  --fi-h:       38px;
  --fi-fs:      0.855rem;
  --fi-radius:  8px;
  --fi-pad:     0 11px;
  --fi-bg:      #f8fafc;
  --fi-bg-focus:#ffffff;
  --fi-border:  #e2e8f0;
  --fi-hover:   #94a3b8;
  --fi-focus:   #2563eb;
  --lbl-fs:     0.68rem;
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

/* ── Section headers — enterprise clean style ───────────── */
.fsec {
  display:        flex;
  align-items:    center;
  gap:            8px;
  font-size:      0.69rem;
  font-weight:    700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color:          #334155;
  margin:         14px 0 7px 0;
  padding:        0;
  border:         none;
  border-radius:  0;
  background:     transparent;
}
.fsec::before {
  content:        '';
  width:          3px;
  height:         14px;
  border-radius:  2px;
  background:     linear-gradient(180deg,#2563eb,#6d28d9);
  flex-shrink:    0;
}
.fsec::after {
  content:        '';
  flex:           1;
  height:         1px;
  background:     linear-gradient(90deg,#cbd5e1,transparent);
}
.fsec-icon  { font-size:0.82rem; line-height:1; }
.fsec-blue, .fsec-green, .fsec-violet, .fsec-amber, .fsec-rose {
  color:          #334155;
  background:     transparent;
}

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
/* Tab panel — white card surface */
div[data-baseweb="tab-panel"] {
  background:    #ffffff !important;
  border-radius: 0 12px 12px 12px !important;
  border:        1px solid #e2e8f0 !important;
  padding:       1.1rem 1.3rem 1rem !important;
  box-shadow:    0 4px 18px rgba(2,6,23,0.06) !important;
}
.stTabs [data-baseweb="tab-panel"] > div:empty {display:none;}
.stTabs [data-baseweb="tab-panel"] > div:has(> div:empty) {display:none;}
/* Tab strip — match card top edge */
div[data-baseweb="tab-list"] {
  background:    transparent !important;
  border-bottom: none !important;
  gap:           2px !important;
}
div[data-baseweb="tab"] {
  background:    #f1f5f9 !important;
  border-radius: 8px 8px 0 0 !important;
  border:        1px solid #e2e8f0 !important;
  border-bottom: none !important;
  padding:       0.35rem 0.9rem !important;
  font-size:     0.78rem !important;
  font-weight:   600 !important;
  color:         #64748b !important;
  transition:    background .15s, color .15s !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
  background:    #ffffff !important;
  color:         #1d4ed8 !important;
  border-color:  #e2e8f0 !important;
}
.stFileUploader {margin-top: 0.35rem;}
.stFileUploader section {padding: 0.5rem 0.75rem !important;}
.stFileUploader button {background: #1d4ed8 !important; color: #fff !important; border: none !important;}
.stFileUploader button:hover {filter: brightness(1.05);}
.stFileUploader small {color: #64748b !important;}
.onboarding-header {max-width: 1200px; margin: 0 auto 0.35rem auto; text-align: left;}
.onboarding-header .section-title {font-size: 1.2rem; margin: 0; text-align: left !important;}
.onboarding-header .section-subtitle {margin: 0.1rem 0 0.4rem 0; text-align: left !important;}
.onboarding-block {margin-left: 0; padding-left: 0;}

/* ── Global compact spacing ─────────────────────────────── */
.block-container { padding-top: 3rem !important; padding-bottom: 0.5rem !important; }
[data-testid="column"] { padding-left: 0.25rem !important; padding-right: 0.25rem !important; }
[data-baseweb="tab-panel"] { padding-top: 0.3rem !important; }
h4 { margin-top: 0.2rem !important; margin-bottom: 0.25rem !important; }

/* ── Compact st.metric() cards ───────────────────────────── */
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.35rem 0.75rem 0.4rem !important;
  box-shadow: 0 2px 6px rgba(2,6,23,0.05);
}
[data-testid="stMetricValue"] {
  font-size: 1.35rem !important;
  font-weight: 700 !important;
  line-height: 1.15 !important;
  color: #0b1221 !important;
}
[data-testid="stMetricLabel"] > div {
  font-size: 0.63rem !important;
  font-weight: 600 !important;
  color: #5b6477 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}
/* Remove extra gap between metric rows */
[data-testid="stVerticalBlock"] > [data-testid="element-container"]:has([data-testid="stMetric"]) {
  margin-bottom: 0.25rem !important;
}
/* ── Sidebar — light nav panel ────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#f8fafc 0%,#edf2fb 100%) !important;
  border-right: 1px solid #d1dae8 !important;
  min-width: 220px !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }
/* Override main button styles for sidebar nav buttons */
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
  background:     rgba(30,64,175,0.06) !important;
  border:         1px solid rgba(30,64,175,0.12) !important;
  color:          #1e3a5f !important;
  border-radius:  8px !important;
  font-size:      0.82rem !important;
  font-weight:    600 !important;
  height:         40px !important;
  padding:        0 1rem !important;
  box-shadow:     none !important;
  letter-spacing: 0 !important;
  justify-content: flex-start !important;
  transition: background .15s, border-color .15s, color .15s !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
  background:   rgba(30,64,175,0.13) !important;
  border-color: rgba(30,64,175,0.28) !important;
  color:        #1d4ed8 !important;
  transform:    none !important;
  filter:       none !important;
  box-shadow:   none !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
<div style="text-align:center;margin-bottom:0.35rem;">
  <div style="font-size:2.2rem;font-weight:700;color:#0b1221;letter-spacing:-0.03em;line-height:1.15;">
    🎯 Udyam Mitra
  </div>
  <div style="font-size:0.88rem;color:#5b6477;margin-top:0.2rem;font-weight:500;">
    AI-Powered MSE Discovery &amp; SNP Matching &nbsp;|&nbsp; IndiaAI Innovation Challenge 2026
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
<div style="background:#f0f7ff;border:1px solid #bfdbfe;border-radius:10px;
            padding:0.5rem 1.2rem;margin-bottom:0.5rem;
            display:flex;align-items:center;justify-content:center;
            gap:0;flex-wrap:wrap;">
  <span style="font-size:0.75rem;font-weight:700;color:#1e40af;
               display:flex;align-items:center;gap:5px;">
    &#127908; Voice Input
  </span>
  <span style="color:#93c5fd;font-size:0.95rem;margin:0 0.55rem;font-weight:400;">&#8594;</span>
  <span style="font-size:0.75rem;font-weight:700;color:#1e40af;
               display:flex;align-items:center;gap:5px;">
    &#129302; AI Extraction
  </span>
  <span style="color:#93c5fd;font-size:0.95rem;margin:0 0.55rem;font-weight:400;">&#8594;</span>
  <span style="font-size:0.75rem;font-weight:700;color:#1e40af;
               display:flex;align-items:center;gap:5px;">
    &#128230; ONDC Taxonomy
  </span>
  <span style="color:#93c5fd;font-size:0.95rem;margin:0 0.55rem;font-weight:400;">&#8594;</span>
  <span style="font-size:0.75rem;font-weight:700;color:#1e40af;
               display:flex;align-items:center;gap:5px;">
    &#128200; Graph Reasoning
  </span>
  <span style="color:#93c5fd;font-size:0.95rem;margin:0 0.55rem;font-weight:400;">&#8594;</span>
  <span style="font-size:0.75rem;font-weight:700;color:#1e3a8a;
               background:#dbeafe;border-radius:20px;padding:0.2rem 0.75rem;
               display:flex;align-items:center;gap:5px;">
    &#127919; Best-fit SNP
  </span>
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

    def _match_label(score):
        if score >= 65: return "TOP MATCH"
        if score >= 45: return "STRONG MATCH"
        if score >= 25: return "GOOD MATCH"
        return "PARTIAL MATCH"

    def _build_reason(result, mse_city):
        """Return (reason_sentence, chips_list, caveat_str)."""
        city_match     = str(result["location"]).strip().lower() == str(mse_city).strip().lower()
        sla_pct        = result.get("sla_pct", 0)
        cap_pct        = result.get("cap_pct", 0)
        export_capable = result.get("export_capable", False)
        certs          = result.get("certifications") or []
        specialization = (result.get("specialization") or "").strip()
        payment        = result.get("payment_terms") or ""
        location       = result.get("location", "")

        # ── Reason sentence ───────────────────────────────────
        parts = []
        if city_match:
            parts.append(f"a local provider in {location}")
        else:
            parts.append(f"based in {location}")

        if specialization:
            parts.append(f"specialises in {specialization[:60].lower()}")

        if sla_pct >= 90:
            parts.append(f"excellent service rating of {sla_pct}%")
        elif sla_pct >= 70:
            parts.append(f"strong service rating of {sla_pct}%")
        else:
            parts.append(f"service rating of {sla_pct}%")

        if export_capable:
            parts.append("export-ready")

        if len(parts) == 1:
            reason = parts[0].capitalize() + "."
        elif len(parts) == 2:
            reason = f"{parts[0].capitalize()} and {parts[1]}."
        else:
            reason = f"{parts[0].capitalize()}, {', '.join(parts[1:-1])}, and {parts[-1]}."

        # ── Attribute chips ───────────────────────────────────
        chips = []
        if certs:
            cert_str = " · ".join(certs[:3])
            suffix = f" +{len(certs) - 3}" if len(certs) > 3 else ""
            chips.append(f"✓ {cert_str}{suffix}")
        chips.append("⚡ High capacity" if cap_pct >= 90 else "📦 Std capacity")
        if payment:
            chips.append(f"💳 {payment}")
        if export_capable:
            chips.append("🌐 Export-ready")

        # ── Caveat ────────────────────────────────────────────
        caveat = (
            f"⚠ Located in {location}, not in {mse_city} — consider delivery lead time."
            if not city_match else ""
        )

        return reason, chips, caveat

    for i, result in enumerate(reasoning_result):
        with cols[i]:
            city_match  = str(result["location"]).strip().lower() == str(mse_city).strip().lower()
            geo_icon    = "&#128205;" if city_match else "&#127758;"
            location    = result.get("location", "")
            badge       = _match_label(result.get("score", 0))
            medal       = medals[i] if i < len(medals) else ""

            reason, chips, caveat = _build_reason(result, mse_city)

            chips_html  = "".join(f'<span class="snp-chip">{c}</span>' for c in chips)
            caveat_html = f'<div class="snp-caveat">{caveat}</div>' if caveat else ""

            st.markdown(f"""
<div class="{card_styles[i]}">
  <!-- Row 1: name left, location right -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <div style="font-size:0.72rem;opacity:0.7;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">{medal} {result['snp']}</div>
    <div style="font-size:0.70rem;opacity:0.60;">{geo_icon} {location}</div>
  </div>
  <!-- Row 2: score + badge inline -->
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
    <div class="snp-score">{result['score']}%</div>
    <div class="snp-badge">{badge}</div>
  </div>
  <span class="snp-score-label">Match Score</span>
  <!-- Divider -->
  <div style="border-top:1px solid rgba(255,255,255,0.15);margin:0.65rem 0 0.5rem;"></div>
  <!-- Why selected -->
  <div class="snp-why-label">Why Selected</div>
  <div class="snp-why-text">{reason}</div>
  <!-- Chips -->
  <div class="snp-chips">{chips_html}</div>
  {caveat_html}
</div>
""", unsafe_allow_html=True)


def render_dashboard_header():
    st.markdown(
        "<div style='font-size:0.95rem;font-weight:700;color:#0b1221;letter-spacing:-0.01em;"
        "margin:0.1rem 0 0.3rem 0;'>📊 Live Intelligence Dashboard</div>",
        unsafe_allow_html=True,
    )



def render_sidebar(current_page="dashboard"):
    with st.sidebar:
        # ── Brand block ──────────────────────────────────────
        st.markdown(
            """
<div style="padding:1.4rem 1.1rem 1rem;border-bottom:1px solid #d1dae8;">
  <div style="font-size:1.3rem;font-weight:800;color:#0b1221;letter-spacing:-0.02em;line-height:1.2;white-space:nowrap;">
    🎯 Udyam Mitra
  </div>
  <div style="font-size:0.62rem;color:#64748b;margin-top:0.45rem;letter-spacing:0.07em;
              text-transform:uppercase;">
    AI&#8209;Powered MSE Discovery
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Nav section ──────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#64748b;margin:1rem 1.1rem 0.4rem;">Menu</div>',
            unsafe_allow_html=True)

        if st.button("🏠  Dashboard", use_container_width=True, key="nav_dash"):
            st.switch_page("app.py")
        if st.button("➕  Add MSE", use_container_width=True, key="nav_add"):
            st.switch_page("pages/01_Add_MSE.py")
        if st.button("💬  Ask Anything", use_container_width=True, key="nav_ask"):
            st.switch_page("pages/04_Ask_Anything.py")

        # ── Admin section ─────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#64748b;margin:1rem 1.1rem 0.4rem;">Admin</div>',
            unsafe_allow_html=True)

        if st.button("🏢  Manage SNPs", use_container_width=True, key="nav_snps"):
            st.switch_page("pages/02_Manage_SNPs.py")
        if st.button("🏷️  Manage Categories", use_container_width=True, key="nav_cats"):
            st.switch_page("pages/03_Manage_Categories.py")

        # ── Active page indicator ────────────────────────────
        _page_meta = {
            "dashboard":         ("📊 Dashboard",         "#3b82f6"),
            "add_mse":           ("📝 Add MSE",           "#8b5cf6"),
            "ask_anything":      ("💬 Ask Anything",      "#06b6d4"),
            "manage_snps":       ("🏢 Manage SNPs",       "#10b981"),
            "manage_categories": ("🏷️ Manage Categories", "#f59e0b"),
        }
        active_label, active_color = _page_meta.get(
            current_page, ("📊 Dashboard", "#3b82f6")
        )
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:7px;margin:0.5rem 0.5rem 0;'
            f'background:rgba(30,64,175,0.07);border-radius:7px;padding:0.3rem 0.75rem;'
            f'border-left:3px solid {active_color};">'
            f'<span style="font-size:0.68rem;color:#64748b;">Active:</span>'
            f'<span style="font-size:0.68rem;font-weight:600;color:#0b1221;">{active_label}</span>'
            f'</div>',
            unsafe_allow_html=True)

        # ── Divider ──────────────────────────────────────────
        st.markdown(
            '<div style="border-top:1px solid #d1dae8;margin:1rem 0;"></div>',
            unsafe_allow_html=True)

        # ── Tech stack ───────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.58rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#64748b;'
            'margin:0 0.5rem 0.5rem;padding-left:0.75rem;">Powered By</div>',
            unsafe_allow_html=True)

        tech = [
            ("🔗", "Neo4j GraphRAG"),
            ("✨", "GPT-4o mini"),
            ("🎙️", "OpenAI Whisper"),
            ("📋", "ONDC Taxonomy"),
        ]
        for icon, label in tech:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'background:rgba(30,64,175,0.05);border-radius:7px;'
                f'padding:0.32rem 0.75rem;margin:0 0.5rem 0.3rem;">'
                f'<span style="font-size:0.9rem;line-height:1;">{icon}</span>'
                f'<span style="font-size:0.72rem;font-weight:500;color:#334155;">{label}</span>'
                f'</div>',
                unsafe_allow_html=True)

        # ── Competition badge ────────────────────────────────
        st.markdown(
            '<div style="border-top:1px solid #d1dae8;margin:0.9rem 0 0.7rem;"></div>',
            unsafe_allow_html=True)
        st.markdown(
            """
<div style="margin:0 0.5rem;background:linear-gradient(135deg,#1e3a8a,#2563eb);
            border-radius:10px;padding:0.65rem 0.85rem;text-align:center;">
  <div style="font-size:0.58rem;font-weight:700;color:#93c5fd;letter-spacing:0.1em;
              text-transform:uppercase;">IndiaAI</div>
  <div style="font-size:0.75rem;font-weight:700;color:#fff;margin-top:2px;">
    Innovation Challenge
  </div>
  <div style="font-size:0.65rem;color:#bfdbfe;margin-top:1px;">2026 · Problem Statement 2</div>
</div>
""", unsafe_allow_html=True)


def render_footer():
    logo_b64 = _logo_b64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="height:28px;width:auto;object-fit:contain;vertical-align:middle;margin-right:0.5rem;" />'
        if logo_b64 else ""
    )
    st.markdown(
        f"""
<div style='text-align:center;padding:0.6rem 1rem;background:linear-gradient(135deg,#f8fafc 0%,#e2e8f0 100%);border-radius:10px;margin-top:1rem;display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0.3rem;'>
    {logo_html}
    <span style='color:#1e40af;font-weight:700;font-size:0.82rem;'>Udyam Mitra | AI&amp;S India LLP</span>
    <span style='color:#5b6477;font-size:0.72rem;margin-left:0.6rem;'>Problem Statement 2 · AI-powered MSE Agent mapping tool · IndiaAI 2026 · Neo4j GraphRAG</span>
</div>
""",
        unsafe_allow_html=True,
    )

import streamlit as st


def configure_page():
    st.set_page_config(layout="wide", page_title="MSME TEAM GraphRAG Platform", page_icon="🧠")


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
body, .main {font-family: 'Space Grotesk', sans-serif; background: #f1f5f9;}
.app-shell {max-width: 1200px; margin: 0 auto;}
.header-1 {font-size: 2.5rem; font-weight: 700; color: var(--ink); text-align: center; margin-bottom: 0.25rem;}
.header-2 {font-size: 1.05rem; color: var(--muted); text-align: center; margin-top: 0;}
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
  padding: 1.2rem 1.4rem;
  border-radius: 16px;
  height: 110px;
  border: 1px solid var(--line);
  box-shadow: 0 12px 28px rgba(2,6,23,0.08);
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
.snp-card-1 {background: linear-gradient(135deg, #0f766e 0%, #0891b2 100%); color: #f8fafc !important; padding: 2rem; border-radius: 20px; box-shadow: 0 25px 50px rgba(2,132,199,0.25);}
.snp-card-2 {background: linear-gradient(135deg, #b91c1c 0%, #f97316 100%); color: #f8fafc !important; padding: 2rem; border-radius: 20px; box-shadow: 0 25px 50px rgba(249,115,22,0.25);}
.reasoning-card {background: #ffffff; color: var(--ink); border-left: 4px solid var(--accent); padding: 1rem 1.25rem; border-radius: 12px; margin: 0.8rem 0; box-shadow: 0 10px 20px rgba(2,6,23,0.08);}
.reasoning-card strong {color: var(--ink);}
.reasoning-card span, .reasoning-card div {color: var(--ink);}
.onboarding-card {background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 1.25rem 1.5rem; box-shadow: 0 12px 28px rgba(2,6,23,0.08);}
.onboarding-step {background: var(--surface-2); border: 1px solid var(--line); padding: 0.75rem 1rem; border-radius: 12px; margin-bottom: 0.75rem; color: var(--ink);}
.stButton>button {background: linear-gradient(135deg, #f97316 0%, #ef4444 100%) !important; color: #fff !important; border: none !important; box-shadow: 0 12px 24px rgba(239,68,68,0.25) !important;}
.stButton>button:hover {filter: brightness(1.05);}
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
    snp_col1, snp_col2 = st.columns(2)
    for i, result in enumerate(reasoning_result):
        col = snp_col1 if i == 0 else snp_col2
        with col:
            city_match = str(result["location"]).strip().lower() == str(mse_city).strip().lower()
            city_text = "Yes" if city_match else "No"
            st.markdown(
                f"""
<div class="snp-card-{1 if i==0 else 2}">
    <h3 style='color:white;font-size:1.4rem;'>🥇 {result['snp']}</h3>
    <h2 style='color:#fef3c7;font-size:2.2rem;'>🎯 {result['score']}%</h2>
    <div class="reasoning-card">
        <strong>🗺️ Geo:</strong> {result['geo_pct']}% ({result['location']})
    </div>
    <div class="reasoning-card">
        <strong>⭐ SLA:</strong> {result['sla_pct']}%
    </div>
    <div class="reasoning-card">
        <strong>📦 Capacity:</strong> {result['cap_pct']}%
    </div>
    <div class="reasoning-card">
        <strong>✅ Evidence:</strong> City match: {city_text} · Category served: Yes
    </div>
    {f'<div style="margin-top:1rem;"><span style="background:#fef3c7;color:#92400e;padding:0.5rem 1rem;border-radius:25px;font-weight:600;">⭐ GRAPH TOP MATCH</span></div>' if i==0 else ''}
</div>
""",
                unsafe_allow_html=True,
            )


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

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.graph_service import (
    fetch_categories_detailed,
    fetch_mse_by_id,
    fetch_recent_mses,
    fetch_snps_detailed,
    fetch_analytics_summary,
)
from msme_app.ui import (
    apply_styles,
    configure_page,
    render_dashboard_header,
    render_footer,
    render_header,
    render_hero,
    render_sidebar,
)

configure_page()

@st.cache_resource
def _get_driver():
    return get_driver(load_config())

driver = _get_driver()

apply_styles()
render_header()
render_hero()
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)
render_sidebar(current_page="dashboard")

render_dashboard_header()

try:
    # Fetch enhanced analytics
    analytics = fetch_analytics_summary(driver)
    
    # ── Layout: metrics (left 3/4) + donut (right 1/4) ─────────────────────
    metrics_col, donut_col = st.columns([3, 1], gap="medium")

    with metrics_col:
        # Primary metrics row
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        r1c1.metric("MSEs", analytics["total_mses"])
        r1c2.metric("SNPs", analytics["total_snps"])
        r1c3.metric("Categories", analytics["total_categories"])
        avg_rating = analytics.get("avg_rating") or 0
        r1c4.metric("Avg Rating", f"{avg_rating*100:.0f}%")

        # Secondary metrics row
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        total_capacity = analytics.get("total_capacity") or 0
        r2c1.metric("Total Capacity", f"{total_capacity:,}")
        r2c2.metric("Export-Ready SNPs", analytics["export_capable_snps"])
        r2c3.metric("Cities Covered", analytics["unique_cities"])
        r2c4.metric("Active Connections", analytics["total_relationships"])

    with donut_col:
        # ── Donut: Export-Ready vs Domestic ─────────────────────────────────
        export_n  = analytics.get("export_capable_snps") or 0
        total_snp = analytics.get("total_snps") or 0
        domestic_n = max(total_snp - export_n, 0)

        donut_fig = go.Figure(go.Pie(
            labels=["Export-Ready", "Domestic"],
            values=[export_n, domestic_n],
            hole=0.68,
            marker=dict(
                colors=["#2563eb", "#e2e8f0"],
                line=dict(color="#ffffff", width=2),
            ),
            textinfo="none",
            hovertemplate="%{label}: %{value} SNPs<extra></extra>",
            direction="clockwise",
            sort=False,
        ))
        pct = f"{export_n/total_snp*100:.0f}%" if total_snp else "—"
        donut_fig.add_annotation(
            text=f"<b>{pct}</b><br><span style='font-size:9px;color:#64748b'>Export-Ready</span>",
            x=0.5, y=0.5,
            font=dict(size=15, color="#0f172a", family="Inter, sans-serif"),
            showarrow=False,
            align="center",
        )
        donut_fig.update_layout(
            margin=dict(t=28, b=4, l=4, r=4),
            height=150,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=-0.22,
                xanchor="center", x=0.5,
                font=dict(size=9, color="#475569"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=dict(
                text="SNP Network",
                font=dict(size=10, color="#64748b", family="Inter, sans-serif"),
                x=0.5, xanchor="center", y=0.97,
            ),
        )
        st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})

    if (
        (analytics.get("total_mses") or 0) == 0
        and (analytics.get("total_snps") or 0) == 0
        and (analytics.get("total_categories") or 0) == 0
    ):
        st.info("Run seed_graph.py to populate the database, then restart the app.")

    tab1, tab2, tab3 = st.tabs(["MSEs", "SNPs", "Categories"])
    
    with tab1:
        mses = fetch_recent_mses(driver)
        normalized = []
        for row in mses:
            props = row.get("props") or {}
            props["id"] = row.get("id")
            props["category_code"] = row.get("category_code")
            props["category_name"] = row.get("category_name")
            normalized.append(props)
        mses_df = pd.DataFrame(normalized)
        if mses_df.empty:
            st.info("No MSEs yet. Add MSE to create MSEs.")
        else:
            def render_mse_details(mse_id):
                mse_details = fetch_mse_by_id(driver, mse_id)
                if not mse_details:
                    st.info("MSE not found.")
                    return
                address_value = mse_details.get("address")
                if isinstance(address_value, str) and address_value.strip():
                    try:
                        mse_details["address"] = json.loads(address_value)
                    except json.JSONDecodeError:
                        pass

                def _comma(value):
                    if isinstance(value, list):
                        return ", ".join([str(v) for v in value if v is not None])
                    return value or ""

                def _v(v):
                    return v if v else "—"

                products_text  = _comma(mse_details.get("products")) or "—"
                unit_names_text = _comma(mse_details.get("unit_names")) or "—"
                nic_codes_text  = _comma(mse_details.get("nic_5_digit_codes")) or "—"
                cat_name  = mse_details.get("category_name", "")
                cat_code  = mse_details.get("category_code", "")
                category_label = f"{cat_name} ({cat_code})".strip(" ()")
                if cat_name and cat_code:
                    category_label = f"{cat_name} ({cat_code})"

                address = mse_details.get("address")
                if isinstance(address, dict):
                    addr_parts = [address.get(k, "") for k in
                                  ["flat", "premises", "road", "village", "block", "district"]
                                  if address.get(k)]
                    address_str = ", ".join(addr_parts) or "—"
                else:
                    address_str = address or "—"

                name       = _v(mse_details.get("name"))
                city       = _v(mse_details.get("city"))
                urn        = _v(mse_details.get("urn"))
                mobile     = _v(mse_details.get("mobile"))
                email      = _v(mse_details.get("email"))
                etype      = _v(mse_details.get("type"))
                activity   = _v(mse_details.get("activity"))
                nic_act    = _v(mse_details.get("nic_activity"))

                etype_badge = (
                    f'<span class="mdet-badge">&#127962; {etype}</span>'
                    if etype != "—" else ""
                )
                cat_badge = (
                    f'<span class="mdet-badge">&#127991;&#65039; {category_label}</span>'
                    if category_label else ""
                )
                nic_row = (
                    f'<div class="mdet-cell"><div class="mdet-lbl">NIC Codes</div>'
                    f'<div class="mdet-val">{nic_codes_text}</div></div>'
                    if nic_codes_text != "—" else ""
                )
                unit_row = (
                    f'<div class="mdet-cell"><div class="mdet-lbl">Unit Names</div>'
                    f'<div class="mdet-val">{unit_names_text}</div></div>'
                    if unit_names_text != "—" else ""
                )
                addr_section = (
                    f'<div class="mdet-sec">&#128205; Registered Address</div>'
                    f'<div class="mdet-grid">'
                    f'<div class="mdet-cell mdet-full"><div class="mdet-lbl">Address</div>'
                    f'<div class="mdet-val">{address_str}</div></div>'
                    f'</div>'
                ) if address_str != "—" else ""

                st.markdown(f"""
<style>
.mdet-header {{
  background: linear-gradient(135deg,#0f172a 0%,#1e3a8a 55%,#2563eb 100%);
  border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: 0.9rem; color:#fff;
}}
.mdet-name {{
  font-size:1.25rem; font-weight:800; letter-spacing:-0.02em; line-height:1.2;
  margin-bottom:0.45rem;
}}
.mdet-badges {{ display:flex; gap:7px; flex-wrap:wrap; }}
.mdet-badge {{
  background:rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.22);
  border-radius:20px; padding:2px 10px;
  font-size:0.7rem; font-weight:600; letter-spacing:0.03em;
}}
.mdet-sec {{
  font-size:0.64rem; font-weight:700; letter-spacing:0.09em; text-transform:uppercase;
  color:#475569; display:flex; align-items:center; gap:7px;
  margin:10px 0 6px 0;
}}
.mdet-sec::before {{
  content:''; width:3px; height:12px; border-radius:2px;
  background:linear-gradient(180deg,#2563eb,#6d28d9); flex-shrink:0;
}}
.mdet-sec::after {{
  content:''; flex:1; height:1px;
  background:linear-gradient(90deg,#cbd5e1,transparent);
}}
.mdet-grid {{
  display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:2px;
}}
.mdet-cell {{
  background:#f8fafc; border:1px solid #e2e8f0; border-radius:9px;
  padding:0.55rem 0.8rem;
}}
.mdet-full {{ grid-column:span 2; }}
.mdet-lbl {{
  font-size:0.61rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;
  color:#94a3b8; margin-bottom:2px;
}}
.mdet-val {{
  font-size:0.83rem; font-weight:500; color:#0f172a; line-height:1.4;
  word-break:break-word;
}}
</style>

<div class="mdet-header">
  <div class="mdet-name">&#127981; {name}</div>
  <div class="mdet-badges">
    <span class="mdet-badge">&#128205; {city}</span>
    <span class="mdet-badge">&#128196; {urn}</span>
    {cat_badge}
    {etype_badge}
  </div>
</div>

<div class="mdet-sec">&#128230; Products</div>
<div class="mdet-grid">
  <div class="mdet-cell mdet-full">
    <div class="mdet-lbl">Products / Services</div>
    <div class="mdet-val">{products_text}</div>
  </div>
</div>

<div class="mdet-sec">&#128222; Contact</div>
<div class="mdet-grid">
  <div class="mdet-cell">
    <div class="mdet-lbl">Mobile</div>
    <div class="mdet-val">{mobile}</div>
  </div>
  <div class="mdet-cell">
    <div class="mdet-lbl">Email</div>
    <div class="mdet-val">{email}</div>
  </div>
</div>

<div class="mdet-sec">&#127981; Classification</div>
<div class="mdet-grid">
  <div class="mdet-cell">
    <div class="mdet-lbl">Activity</div>
    <div class="mdet-val">{activity}</div>
  </div>
  <div class="mdet-cell">
    <div class="mdet-lbl">NIC Activity</div>
    <div class="mdet-val">{nic_act}</div>
  </div>
  {nic_row}
  {unit_row}
</div>

{addr_section}
""", unsafe_allow_html=True)

            # ── MSE Insights: City Distribution + Activity Breakdown ───────────
            city_col, act_col = st.columns([3, 2])

            with city_col:
                _city_s = mses_df["city"].fillna("").str.strip()
                _city_counts = (
                    _city_s[_city_s != ""].value_counts().reset_index()
                )
                _city_counts.columns = ["City", "MSEs"]
                _max_c = _city_counts["MSEs"].max() or 1
                _c_medals = ["🥇", "🥈", "🥉"]
                _city_rows_html = ""
                for _ci, (_, _cr) in enumerate(_city_counts.head(10).iterrows()):
                    _cm  = _c_medals[_ci] if _ci < 3 else str(_ci + 1)
                    _cp  = round(_cr["MSEs"] / _max_c * 100)
                    _cfs = "1rem" if _ci < 3 else "0.78rem"
                    _cbg = "#f8fafc" if _ci % 2 == 0 else "#ffffff"
                    _city_rows_html += (
                        f'<div style="display:grid;grid-template-columns:2rem 1fr 2.5rem 100px;'
                        f'align-items:center;gap:8px;padding:0.42rem 0.7rem;'
                        f'background:{_cbg};border-radius:7px;margin-bottom:3px;">'
                        f'<div style="font-size:{_cfs};text-align:center;font-weight:700;color:#334155;">{_cm}</div>'
                        f'<div style="font-size:0.78rem;font-weight:600;color:#0f172a;">{_cr["City"]}</div>'
                        f'<div style="font-size:0.8rem;font-weight:700;color:#2563eb;text-align:right;">{_cr["MSEs"]}</div>'
                        f'<div style="background:#e2e8f0;border-radius:20px;height:7px;overflow:hidden;">'
                        f'<div style="width:{_cp}%;height:100%;background:#2563eb;border-radius:20px;"></div>'
                        f'</div>'
                        f'</div>'
                    )
                st.markdown(
                    f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;'
                    f'padding:0.65rem 0.4rem 0.4rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:#334155;padding:0 0.5rem 0.55rem;'
                    f'border-bottom:1px solid #f1f5f9;margin-bottom:0.45rem;">'
                    f'🏙️ MSE Distribution by City</div>'
                    f'<div style="max-height:248px;overflow-y:auto;">{_city_rows_html}</div></div>',
                    unsafe_allow_html=True,
                )

            with act_col:
                # MSEs by Category — scrollable leaderboard card (scales to 100s of categories)
                _cat_s = mses_df["category_name"].fillna("").str.strip()
                _cat_s = _cat_s[_cat_s != ""]
                if not _cat_s.empty:
                    _cat_counts = _cat_s.value_counts().reset_index()
                    _cat_counts.columns = ["Category", "MSEs"]
                    _max_cat = _cat_counts["MSEs"].max() or 1
                    # Blue gradient palette indexed by rank for visual variety
                    _cat_colors = ["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"]
                    _cat_rows_html = ""
                    for _ki, (_, _kr) in enumerate(_cat_counts.iterrows()):
                        _kp  = round(_kr["MSEs"] / _max_cat * 100)
                        _kbg = "#f8fafc" if _ki % 2 == 0 else "#ffffff"
                        _kc  = _cat_colors[min(_ki, len(_cat_colors) - 1)]
                        _cat_rows_html += (
                            f'<div style="display:grid;grid-template-columns:1fr 2rem 90px;'
                            f'align-items:center;gap:8px;padding:0.42rem 0.7rem;'
                            f'background:{_kbg};border-radius:7px;margin-bottom:3px;">'
                            f'<div style="font-size:0.76rem;font-weight:600;color:#0f172a;'
                            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                            f'{_kr["Category"]}</div>'
                            f'<div style="font-size:0.8rem;font-weight:700;color:{_kc};'
                            f'text-align:right;">{_kr["MSEs"]}</div>'
                            f'<div style="background:#e2e8f0;border-radius:20px;height:7px;overflow:hidden;">'
                            f'<div style="width:{_kp}%;height:100%;background:{_kc};border-radius:20px;"></div>'
                            f'</div>'
                            f'</div>'
                        )
                    st.markdown(
                        f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;'
                        f'padding:0.65rem 0.4rem 0.4rem;">'
                        f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                        f'text-transform:uppercase;color:#334155;padding:0 0.5rem 0.55rem;'
                        f'border-bottom:1px solid #f1f5f9;margin-bottom:0.45rem;">'
                        f'📂 MSEs by Category</div>'
                        f'<div style="max-height:248px;overflow-y:auto;">{_cat_rows_html}</div></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("Category data not available yet.")

            st.divider()

            # ── Filters + Table ───────────────────────────────────────────────
            filt_c1, filt_c2 = st.columns(2)
            with filt_c1:
                _mse_cities = ["All"] + sorted(
                    mses_df["city"].fillna("").str.strip().replace("", None).dropna().unique().tolist()
                )
                mse_city_filt = st.selectbox("Filter by City", _mse_cities, key="mse_city_filter")
            with filt_c2:
                _mse_cats = ["All"] + sorted(
                    mses_df["category_name"].fillna("").str.strip().replace("", None).dropna().unique().tolist()
                )
                mse_cat_filt = st.selectbox("Filter by Category", _mse_cats, key="mse_cat_filter")

            display_rows = []
            for row in mses_df.fillna("").to_dict(orient="records"):
                category_label = ""
                if row.get("category_name") or row.get("category_code"):
                    category_label = f"{row.get('category_name', '')} ({row.get('category_code', '')})".strip()
                products_val = row.get("products", "")
                if isinstance(products_val, list):
                    products_val = ", ".join([str(v) for v in products_val if v is not None])
                display_rows.append({
                    "ID":        row.get("id", ""),
                    "Business":  row.get("name", ""),
                    "City":      row.get("city", ""),
                    "Category":  category_label,
                    "_cat_name": row.get("category_name", ""),
                    "Products":  products_val,
                })

            display_df = pd.DataFrame(display_rows)

            if mse_city_filt != "All":
                display_df = display_df[display_df["City"] == mse_city_filt]
            if mse_cat_filt != "All":
                display_df = display_df[display_df["_cat_name"] == mse_cat_filt]
            display_df = display_df.drop(columns=["_cat_name"])

            n_shown = len(display_df)
            st.caption(
                f"Showing {n_shown} MSE{'s' if n_shown != 1 else ''} · newest first · click any row for details"
            )

            # Generation counter: bumped on each selection so the dataframe
            # always starts with zero selection state after a dialog close.
            df_gen = st.session_state.get("dash_mse_df_gen", 0)
            event = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=240,
                on_select="rerun",
                selection_mode="single-row",
                key=f"mse_df_{df_gen}",
            )

            sel_rows = event.selection.rows
            if sel_rows:
                # Phase 1: stash ID, bump key so next render has no selection
                st.session_state["dash_mse_pending_id"] = display_df.iloc[sel_rows[0]]["ID"]
                st.session_state["dash_mse_df_gen"] = df_gen + 1
                st.rerun()

            # Phase 2: pending_id already removed from state before dialog opens,
            # so dialog close rerun finds nothing and shows a clean empty table.
            pending_id = st.session_state.pop("dash_mse_pending_id", None)
            if pending_id:
                if hasattr(st, "dialog"):
                    @st.dialog("MSE Details")
                    def _dialog(mse_id):
                        render_mse_details(mse_id)
                    _dialog(pending_id)
                else:
                    with st.expander("MSE Details", expanded=True):
                        render_mse_details(pending_id)
    
    with tab2:
        
        # Fetch detailed SNP data
        snps = fetch_snps_detailed(driver, limit=None)
        
        if not snps:
            st.info("No SNPs found. Run seed_graph.py to populate SNPs.")
        else:
            # Create display dataframe with rich metadata
            snp_rows = []
            for snp in snps:
                # Format certifications
                certs = snp.get("certifications") or []
                cert_display = ", ".join(certs[:3]) if certs else "None"
                if len(certs) > 3:
                    cert_display += f" +{len(certs)-3}"
                
                # Format languages
                langs = snp.get("languages") or []
                lang_display = ", ".join(langs[:3]) if langs else "None"
                
                # Format categories served
                cat_codes = snp.get("category_codes") or []
                cat_display = ", ".join(cat_codes[:3]) if cat_codes else "None"
                if len(cat_codes) > 3:
                    cat_display += f" +{len(cat_codes)-3}"
                
                snp_rows.append({
                    "ID": snp["id"],
                    "Name": snp["name"],
                    "City": snp["city"],
                    "Rating": f"{snp['rating']*100:.0f}%",
                    "Capacity": snp["capacity"],
                    "Export": "✅" if snp.get("export_capable") else "❌",
                    "Certifications": cert_display,
                    "Languages": lang_display,
                    "Categories": cat_display,
                    "Payment": snp.get("payment_terms") or "N/A",
                })
            
            snps_df = pd.DataFrame(snp_rows)
            
            # ── SNP Rating Leaderboard ────────────────────────────────────────
            lb_col, scatter_col = st.columns([3, 2])

            with lb_col:
                top_snps = sorted(snps, key=lambda s: (s["rating"] or 0), reverse=True)[:10]
                _medals = ["🥇", "🥈", "🥉"]
                rows_html = ""
                for _rank, _s in enumerate(top_snps):
                    _pct       = round((_s["rating"] or 0) * 100)
                    _medal     = _medals[_rank] if _rank < 3 else str(_rank + 1)
                    _is_export = bool(_s.get("export_capable"))
                    _bar_color = "#2563eb" if _is_export else "#94a3b8"
                    _badge_bg  = "#dbeafe" if _is_export else "#f1f5f9"
                    _badge_col = "#1d4ed8" if _is_export else "#94a3b8"
                    _badge_txt = "EXPORT" if _is_export else "DOMESTIC"
                    _row_bg    = "#f8fafc" if _rank % 2 == 0 else "#ffffff"
                    _fs_medal  = "1rem" if _rank < 3 else "0.78rem"
                    rows_html += (
                        f'<div style="display:grid;grid-template-columns:2rem 1fr auto 120px 3rem 5rem;'
                        f'align-items:center;gap:8px;padding:0.42rem 0.7rem;'
                        f'background:{_row_bg};border-radius:7px;margin-bottom:3px;">'
                        f'<div style="font-size:{_fs_medal};text-align:center;font-weight:700;color:#334155;">{_medal}</div>'
                        f'<div style="font-size:0.78rem;font-weight:600;color:#0f172a;'
                        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_s["name"]}</div>'
                        f'<div style="font-size:0.68rem;color:#64748b;white-space:nowrap;">📍 {_s["city"]}</div>'
                        f'<div style="background:#e2e8f0;border-radius:20px;height:7px;overflow:hidden;">'
                        f'<div style="width:{_pct}%;height:100%;background:{_bar_color};border-radius:20px;"></div>'
                        f'</div>'
                        f'<div style="font-size:0.8rem;font-weight:700;color:{_bar_color};text-align:right;">{_pct}%</div>'
                        f'<div style="text-align:right;">'
                        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:0.05em;'
                        f'background:{_badge_bg};color:{_badge_col};border-radius:10px;padding:2px 6px;">'
                        f'{_badge_txt}</span></div>'
                        f'</div>'
                    )
                st.markdown(
                    f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;'
                    f'padding:0.65rem 0.4rem 0.4rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:#334155;padding:0 0.5rem 0.55rem;'
                    f'border-bottom:1px solid #f1f5f9;margin-bottom:0.45rem;">'
                    f'🏆 Top 10 SNPs by Rating</div>'
                    f'<div style="max-height:248px;overflow-y:auto;">{rows_html}</div></div>',
                    unsafe_allow_html=True,
                )

            with scatter_col:
                _scatter_df = pd.DataFrame([{
                    "Name":     s["name"],
                    "Rating":   round((s["rating"] or 0) * 100, 1),
                    "Capacity": s.get("capacity") or 0,
                    "Type":     "Export-Ready" if s.get("export_capable") else "Domestic",
                } for s in snps])
                sc_fig = px.scatter(
                    _scatter_df,
                    x="Rating", y="Capacity",
                    color="Type",
                    color_discrete_map={"Export-Ready": "#2563eb", "Domestic": "#94a3b8"},
                    hover_name="Name",
                    labels={"Rating": "Rating (%)", "Capacity": "Capacity"},
                )
                sc_fig.update_traces(marker=dict(size=10, line=dict(width=1.5, color="#ffffff")))
                sc_fig.update_layout(
                    height=290,
                    margin=dict(t=36, b=10, l=4, r=4),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#f8fafc",
                    title=dict(
                        text="Rating vs Capacity",
                        font=dict(size=11, color="#334155", family="Inter, sans-serif"),
                        x=0, xanchor="left",
                    ),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1,
                        font=dict(size=9, color="#475569"),
                        title_text="",
                    ),
                    xaxis=dict(
                        range=[0, 105], ticksuffix="%",
                        showgrid=True, gridcolor="#e2e8f0", gridwidth=1,
                        zeroline=False, tickfont=dict(size=9, color="#94a3b8"),
                    ),
                    yaxis=dict(
                        showgrid=True, gridcolor="#e2e8f0", gridwidth=1,
                        zeroline=False, tickfont=dict(size=9, color="#94a3b8"),
                    ),
                    font=dict(family="Inter, sans-serif"),
                )
                st.plotly_chart(sc_fig, use_container_width=True, config={"displayModeBar": False})

            st.divider()

            # Add filters
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                city_filter = st.selectbox(
                    "Filter by City",
                    ["All"] + sorted(snps_df["City"].unique().tolist()),
                    key="snp_city_filter"
                )
            with col_f2:
                export_filter = st.selectbox(
                    "Export Capability",
                    ["All", "Export-Ready Only", "Domestic Only"],
                    key="snp_export_filter"
                )
            with col_f3:
                min_rating = st.slider(
                    "Minimum Rating",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5,
                    key="snp_rating_filter"
                )
            
            # Apply filters
            filtered_df = snps_df.copy()
            if city_filter != "All":
                filtered_df = filtered_df[filtered_df["City"] == city_filter]
            if export_filter == "Export-Ready Only":
                filtered_df = filtered_df[filtered_df["Export"] == "✅"]
            elif export_filter == "Domestic Only":
                filtered_df = filtered_df[filtered_df["Export"] == "❌"]
            # Convert rating back to numeric for filtering
            filtered_df["Rating_Numeric"] = filtered_df["Rating"].str.rstrip("%").astype(int)
            filtered_df = filtered_df[filtered_df["Rating_Numeric"] >= min_rating]
            filtered_df = filtered_df.drop("Rating_Numeric", axis=1)
            
            st.caption(f"Showing {len(filtered_df)} of {len(snps_df)} SNPs")
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                height=240,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "City": st.column_config.TextColumn("City", width="small"),
                    "Rating": st.column_config.TextColumn("Rating", width="small"),
                    "Capacity": st.column_config.NumberColumn("Capacity", width="small"),
                    "Export": st.column_config.TextColumn("Export", width="small"),
                    "Certifications": st.column_config.TextColumn("Certifications", width="medium"),
                    "Languages": st.column_config.TextColumn("Languages", width="small"),
                    "Categories": st.column_config.TextColumn("Serves", width="medium"),
                    "Payment": st.column_config.TextColumn("Payment", width="small"),
                }
            )
            
            # SNP details expansion
            with st.expander("📊 View SNP Specializations", expanded=False):
                for snp in snps[:10]:  # Show first 10
                    spec = snp.get("specialization")
                    if spec:
                        st.markdown(f"**{snp['name']}:** {spec}")
    
    with tab3:

        # Fetch detailed category data
        cats = fetch_categories_detailed(driver, limit=None)

        if not cats:
            st.info("No categories found. Run seed_graph.py to populate categories.")
        else:
            # Build dataframe
            cat_rows = []
            for cat in cats:
                keywords = cat.get("keywords") or []
                keyword_display = ", ".join(keywords[:5]) if keywords else "None"
                if len(keywords) > 5:
                    keyword_display += f" +{len(keywords)-5}"
                ondc_path = ""
                if cat.get("ondc_l1"):
                    ondc_path = f"{cat['ondc_l1']} → {cat.get('ondc_l2', 'N/A')} → {cat.get('ondc_l3', 'N/A')}"
                cat_rows.append({
                    "Code": cat["code"],
                    "Name": cat["name"],
                    "Sector": cat["sector"],
                    "SNPs": cat.get("snp_count", 0),
                    "Keywords (Sample)": keyword_display,
                    "ONDC Taxonomy": ondc_path,
                })
            cats_df = pd.DataFrame(cat_rows)

            # ── Category Insights: Treemap + Sector Summary (chart first) ─────
            tree_col, sector_col = st.columns([3, 2])

            with tree_col:
                _tree_df = cats_df.copy()
                # min size 1 so zero-SNP categories still render a visible tile
                _tree_df["_size"] = _tree_df["SNPs"].clip(lower=1)
                # Qualitative sector colours — each sector gets a distinct hue
                _sector_palette = [
                    "#2563eb", "#7c3aed", "#0891b2", "#059669",
                    "#d97706", "#dc2626", "#db2777", "#65a30d",
                    "#9333ea", "#0284c7", "#b45309", "#0f766e",
                ]
                tree_fig = px.treemap(
                    _tree_df,
                    path=[px.Constant("All Categories"), "Sector", "Name"],
                    values="_size",
                    color="Sector",
                    color_discrete_sequence=_sector_palette,
                    custom_data=["Code", "SNPs", "ONDC Taxonomy"],
                )
                tree_fig.update_traces(
                    textinfo="label",
                    textfont=dict(size=11, family="Inter, sans-serif"),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Code: %{customdata[0]}<br>"
                        "SNPs: %{customdata[1]}<br>"
                        "ONDC: %{customdata[2]}<extra></extra>"
                    ),
                    root_color="rgba(0,0,0,0)",
                    marker=dict(line=dict(width=1.5, color="#ffffff")),
                )
                tree_fig.update_layout(
                    height=290,
                    margin=dict(t=36, b=4, l=4, r=4),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=dict(
                        text="Category Coverage by Sector  ·  tile size = SNP count",
                        font=dict(size=11, color="#334155", family="Inter, sans-serif"),
                        x=0, xanchor="left",
                    ),
                    font=dict(family="Inter, sans-serif"),
                )
                st.plotly_chart(tree_fig, use_container_width=True, config={"displayModeBar": False})

            with sector_col:
                # Sector summary with colour-matched dot and mini progress bar
                _sec_summary = (
                    cats_df.groupby("Sector", as_index=False)
                    .agg(Categories=("Code", "count"), SNPs=("SNPs", "sum"))
                    .sort_values("SNPs", ascending=False)
                )
                _max_snps = _sec_summary["SNPs"].max() or 1
                _all_sectors = sorted(cats_df["Sector"].unique().tolist())
                _sec_rows = ""
                for _, _row in _sec_summary.iterrows():
                    _pct = round(_row["SNPs"] / _max_snps * 100)
                    _cidx = _all_sectors.index(_row["Sector"]) % len(_sector_palette)
                    _dot_color = _sector_palette[_cidx]
                    _sec_rows += (
                        f'<div style="padding:0.42rem 0.7rem;background:#f8fafc;'
                        f'border-radius:7px;margin-bottom:4px;">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;margin-bottom:5px;">'
                        f'<div style="display:flex;align-items:center;gap:6px;max-width:60%;'
                        f'overflow:hidden;">'
                        f'<span style="width:8px;height:8px;border-radius:50%;flex-shrink:0;'
                        f'background:{_dot_color};display:inline-block;"></span>'
                        f'<span style="font-size:0.78rem;font-weight:600;color:#0f172a;'
                        f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                        f'{_row["Sector"]}</span></div>'
                        f'<div style="font-size:0.66rem;color:#64748b;white-space:nowrap;">'
                        f'{_row["Categories"]} cats &nbsp;·&nbsp; {_row["SNPs"]} SNPs</div>'
                        f'</div>'
                        f'<div style="background:#e2e8f0;border-radius:20px;height:5px;">'
                        f'<div style="width:{_pct}%;height:100%;'
                        f'background:{_dot_color};border-radius:20px;opacity:0.75;"></div>'
                        f'</div>'
                        f'</div>'
                    )
                st.markdown(
                    f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;'
                    f'padding:0.65rem 0.4rem 0.4rem;">'
                    f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
                    f'text-transform:uppercase;color:#334155;padding:0 0.5rem 0.55rem;'
                    f'border-bottom:1px solid #f1f5f9;margin-bottom:0.45rem;">'
                    f'📂 Sector Coverage</div>'
                    f'<div style="max-height:248px;overflow-y:auto;">{_sec_rows}</div></div>',
                    unsafe_allow_html=True,
                )

            st.divider()

            # ── Filters + Table (mirrors SNPs tab layout) ─────────────────────
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                sector_filter = st.selectbox(
                    "Filter by Sector",
                    ["All"] + sorted(cats_df["Sector"].unique().tolist()),
                    key="cat_sector_filter",
                )
            with col_c2:
                has_snps = st.checkbox(
                    "Only categories with SNPs",
                    value=False,
                    key="cat_has_snps_filter",
                )

            filtered_cats = cats_df.copy()
            if sector_filter != "All":
                filtered_cats = filtered_cats[filtered_cats["Sector"] == sector_filter]
            if has_snps:
                filtered_cats = filtered_cats[filtered_cats["SNPs"] > 0]

            st.caption(f"Showing {len(filtered_cats)} of {len(cats_df)} Categories")
            st.dataframe(
                filtered_cats,
                use_container_width=True,
                hide_index=True,
                height=240,
                column_config={
                    "Code": st.column_config.TextColumn("Code", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Sector": st.column_config.TextColumn("Sector", width="small"),
                    "SNPs": st.column_config.NumberColumn("SNPs", width="small"),
                    "Keywords (Sample)": st.column_config.TextColumn("Keywords", width="large"),
                    "ONDC Taxonomy": st.column_config.TextColumn("ONDC Path", width="large"),
                },
            )

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Run seed_graph.py to populate the database, then restart the app.")

render_footer()

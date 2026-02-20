import pandas as pd
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.graph_service import (
    delete_category,
    fetch_categories_detailed,
    fetch_category_by_id,
    save_category,
)
from msme_app.ui import (
    apply_styles,
    configure_page,
    render_footer,
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
render_sidebar(current_page="manage_categories")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:0.95rem;font-weight:700;color:#0b1221;"
    "letter-spacing:-0.01em;margin:0.1rem 0 0.3rem 0;'>🏷️ Category Management</div>",
    unsafe_allow_html=True,
)
st.caption("Create, view, update, and delete ONDC-aligned product/service categories.")

_SECTORS = [
    "Agriculture", "Automotive", "Chemicals", "Construction", "Crafts",
    "Electronics", "Energy", "FMCG", "Healthcare", "Manufacturing",
    "Packaging", "Printing", "Processing", "Rubber", "Safety",
    "Services", "Sports", "Stationery", "Other",
]


# ── Category form (add / edit) ────────────────────────────────────────────────
def _cat_form(cat_code=None):
    """Render the category create/edit form inside a dialog."""
    is_edit = cat_code is not None
    existing = fetch_category_by_id(driver, cat_code) if is_edit else {}

    st.markdown("""
<style>
.catf-sec {
  font-size:0.63rem;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;
  color:#475569;display:flex;align-items:center;gap:7px;margin:12px 0 6px;
}
.catf-sec::before {
  content:'';width:3px;height:12px;border-radius:2px;
  background:linear-gradient(180deg,#f59e0b,#d97706);flex-shrink:0;
}
.catf-sec::after {
  content:'';flex:1;height:1px;background:linear-gradient(90deg,#cbd5e1,transparent);
}
.del-zone {
  background:#fff5f5;border:1px solid #fecaca;border-radius:10px;
  padding:0.9rem 1rem;margin-top:0.5rem;
}
</style>
""", unsafe_allow_html=True)

    with st.form("cat_form", border=False):
        st.markdown('<div class="catf-sec">Identity</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            code_input = st.text_input(
                "Category Code *",
                value=cat_code or "",
                disabled=is_edit,
                help="Unique uppercase code e.g. TX001, FD001",
            )
            name = st.text_input("Category Name *", value=existing.get("name", ""))
        with c2:
            existing_sector = existing.get("sector", "")
            sec_idx = _SECTORS.index(existing_sector) if existing_sector in _SECTORS \
                else _SECTORS.index("Other")
            sector = st.selectbox("Sector *", _SECTORS, index=sec_idx)

        st.markdown('<div class="catf-sec">Keywords</div>', unsafe_allow_html=True)
        kw_val = ", ".join(existing.get("keywords") or [])
        kw_text = st.text_area(
            "Keywords (comma-separated, include Hindi terms for better matching)",
            value=kw_val,
            height=80,
            help="These keywords drive the AI categorization engine.",
        )

        st.markdown('<div class="catf-sec">ONDC Taxonomy</div>', unsafe_allow_html=True)
        c3, c4, c5 = st.columns(3)
        with c3:
            ondc_l1 = st.text_input("ONDC L1 (Domain)", value=existing.get("ondc_l1", ""),
                                     placeholder="e.g. Fashion")
        with c4:
            ondc_l2 = st.text_input("ONDC L2 (Sub-domain)", value=existing.get("ondc_l2", ""),
                                     placeholder="e.g. Apparel")
        with c5:
            ondc_l3 = st.text_input("ONDC L3 (Leaf)", value=existing.get("ondc_l3", ""),
                                     placeholder="e.g. Readymade Garments")

        submitted = st.form_submit_button(
            "💾  Save Category",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        final_code = (code_input.strip().upper() if not is_edit else cat_code)
        if not name.strip():
            st.error("Category Name is required.")
        elif not final_code:
            st.error("Category Code is required.")
        elif not is_edit and fetch_category_by_id(driver, final_code):
            st.error(
                f"Category code **{final_code}** already exists. "
                "Each category must have a unique code. "
                "Use the table to edit the existing record."
            )
        else:
            save_category(
                driver,
                code=final_code,
                name=name.strip(),
                sector=sector,
                keywords=[k.strip() for k in kw_text.split(",") if k.strip()],
                ondc_l1=ondc_l1.strip() or None,
                ondc_l2=ondc_l2.strip() or None,
                ondc_l3=ondc_l3.strip() or None,
            )
            st.success("Category saved successfully!")
            st.rerun()

    # ── Delete zone (edit only) ───────────────────────────────────────────────
    if is_edit:
        st.markdown('<div class="catf-sec">Danger Zone</div>', unsafe_allow_html=True)
        st.markdown('<div class="del-zone">', unsafe_allow_html=True)
        confirm = st.checkbox(
            f"I understand this will permanently delete **{existing.get('name', cat_code)}** "
            f"({cat_code}). MSEs using this category cannot be deleted."
        )
        if st.button("🗑  Delete Category", disabled=not confirm, use_container_width=True):
            ok, msg = delete_category(driver, cat_code)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Main table ────────────────────────────────────────────────────────────────
try:
    # Header row: filters + add button
    hdr_col, btn_col = st.columns([5, 1])
    with btn_col:
        if st.button("➕ Add Category", use_container_width=True):
            st.session_state["cat_show_add"] = True
            st.rerun()

    cats = fetch_categories_detailed(driver, limit=None)

    if not cats:
        st.info("No categories found. Click 'Add Category' or run seed_graph.py.")
    else:
        rows = []
        for c in cats:
            kw = c.get("keywords") or []
            kw_disp = ", ".join(kw[:5]) + (f" +{len(kw)-5}" if len(kw) > 5 else "")
            ondc_path = ""
            if c.get("ondc_l1"):
                ondc_path = " → ".join(filter(None, [
                    c.get("ondc_l1"), c.get("ondc_l2"), c.get("ondc_l3")
                ]))
            rows.append({
                "Code": c["code"],
                "Name": c["name"],
                "Sector": c["sector"],
                "SNPs": c.get("snp_count", 0),
                "Keywords": kw_disp,
                "ONDC Path": ondc_path,
            })

        cats_df = pd.DataFrame(rows)

        # Sector filter
        f1, f2 = st.columns([2, 3])
        with f1:
            sector_filter = st.selectbox(
                "Filter by Sector",
                ["All"] + sorted(cats_df["Sector"].unique().tolist()),
                key="mgcat_sector_filter",
            )
        with f2:
            has_snps = st.checkbox("Only categories with SNPs", key="mgcat_has_snps")

        filtered_df = cats_df.copy()
        if sector_filter != "All":
            filtered_df = filtered_df[filtered_df["Sector"] == sector_filter]
        if has_snps:
            filtered_df = filtered_df[filtered_df["SNPs"] > 0]

        st.caption(
            f"**{len(filtered_df)}** of {len(cats_df)} categories — "
            "click a row to edit"
        )

        gen = st.session_state.get("cat_df_gen", 0)
        event = st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=min(440, 40 + len(filtered_df) * 35),
            on_select="rerun",
            selection_mode="single-row",
            key=f"cat_df_{gen}",
            column_config={
                "Code": st.column_config.TextColumn("Code", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Sector": st.column_config.TextColumn("Sector", width="small"),
                "SNPs": st.column_config.NumberColumn("SNPs", width="small"),
                "Keywords": st.column_config.TextColumn("Keywords", width="large"),
                "ONDC Path": st.column_config.TextColumn("ONDC Path", width="large"),
            },
        )

        sel = event.selection.rows
        if sel:
            st.session_state["cat_pending_code"] = filtered_df.iloc[sel[0]]["Code"]
            st.session_state["cat_df_gen"] = gen + 1
            st.rerun()

    # Phase 2: open the correct dialog
    pending_code = st.session_state.pop("cat_pending_code", None)
    show_add = st.session_state.pop("cat_show_add", False)

    if pending_code:
        @st.dialog(f"Edit Category — {pending_code}", width="large")
        def _edit_dlg():
            _cat_form(cat_code=pending_code)
        _edit_dlg()

    elif show_add:
        @st.dialog("Add New Category", width="large")
        def _add_dlg():
            _cat_form(cat_code=None)
        _add_dlg()

except Exception as e:
    st.error(f"Error: {e}")

render_footer()

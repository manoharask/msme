import pandas as pd
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.graph_service import (
    delete_snp,
    fetch_categories_detailed,
    fetch_snp_by_id,
    fetch_snps_detailed,
    save_snp,
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
render_sidebar(current_page="manage_snps")

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown(
    "<div style='font-size:0.95rem;font-weight:700;color:#0b1221;"
    "letter-spacing:-0.01em;margin:0.1rem 0 0.3rem 0;'>🏢 Seller Network Participants (SNPs)</div>",
    unsafe_allow_html=True,
)
st.caption("Create, view, update, and delete SNPs — ONDC-registered service providers that MSEs are matched to.")

_PAYMENT_OPTIONS = ["Net 15", "Net 30", "Net 45", "Net 60", "Advance", "COD"]


# ── SNP form (add / edit) ─────────────────────────────────────────────────────
def _snp_form(snp_id=None):
    """Render the SNP create/edit form inside a dialog."""
    is_edit = snp_id is not None
    existing = fetch_snp_by_id(driver, snp_id) if is_edit else {}

    cats = fetch_categories_detailed(driver, limit=None)
    all_codes = [c["code"] for c in cats]
    code_label = {c["code"]: f"{c['name']} ({c['code']})" for c in cats}
    existing_cats = existing.get("category_codes") or []

    # Inline card CSS
    st.markdown("""
<style>
.snpf-sec {
  font-size:0.63rem;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;
  color:#475569;display:flex;align-items:center;gap:7px;margin:12px 0 6px;
}
.snpf-sec::before {
  content:'';width:3px;height:12px;border-radius:2px;
  background:linear-gradient(180deg,#2563eb,#6d28d9);flex-shrink:0;
}
.snpf-sec::after {
  content:'';flex:1;height:1px;background:linear-gradient(90deg,#cbd5e1,transparent);
}
.del-zone {
  background:#fff5f5;border:1px solid #fecaca;border-radius:10px;
  padding:0.9rem 1rem;margin-top:0.5rem;
}
</style>
""", unsafe_allow_html=True)

    with st.form("snp_form", border=False):
        st.markdown('<div class="snpf-sec">Basic Information</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sid = st.text_input(
                "SNP ID *",
                value=snp_id or "",
                disabled=is_edit,
                help="Unique identifier e.g. SNP026",
            )
            name = st.text_input("Name *", value=existing.get("name", ""))
        with c2:
            city = st.text_input("City *", value=existing.get("city", ""))
            pt_idx = _PAYMENT_OPTIONS.index(existing["payment_terms"]) \
                if existing.get("payment_terms") in _PAYMENT_OPTIONS else 1
            payment = st.selectbox("Payment Terms", _PAYMENT_OPTIONS, index=pt_idx)

        st.markdown('<div class="snpf-sec">Capacity & Capabilities</div>', unsafe_allow_html=True)
        c3, c4, c5 = st.columns(3)
        with c3:
            rating = st.slider(
                "Rating (%)", 0, 100,
                value=int((existing.get("rating") or 0) * 100),
            )
        with c4:
            capacity = st.number_input(
                "Capacity", min_value=0,
                value=int(existing.get("capacity") or 0),
            )
        with c5:
            export_capable = st.checkbox(
                "Export-Ready",
                value=bool(existing.get("export_capable", False)),
            )

        st.markdown('<div class="snpf-sec">Location (optional)</div>', unsafe_allow_html=True)
        c6, c7 = st.columns(2)
        with c6:
            lat = st.number_input(
                "Latitude", value=float(existing.get("lat") or 0.0),
                format="%.4f",
            )
        with c7:
            lon = st.number_input(
                "Longitude", value=float(existing.get("lon") or 0.0),
                format="%.4f",
            )

        st.markdown('<div class="snpf-sec">Credentials & Specialization</div>', unsafe_allow_html=True)
        certs_val = ", ".join(existing.get("certifications") or [])
        certs_text = st.text_input("Certifications (comma-separated)", value=certs_val)
        langs_val = ", ".join(existing.get("languages") or [])
        langs_text = st.text_input(
            "Languages (comma-separated, use codes: en hi ta te kn mr gu bn ml pa)",
            value=langs_val,
        )
        specialization = st.text_area(
            "Specialization",
            value=existing.get("specialization", ""),
            height=72,
        )

        st.markdown('<div class="snpf-sec">Categories Served</div>', unsafe_allow_html=True)
        selected_cats = st.multiselect(
            "Select categories this SNP serves",
            options=all_codes,
            default=[c for c in existing_cats if c in all_codes],
            format_func=lambda c: code_label.get(c, c),
        )

        submitted = st.form_submit_button(
            "💾  Save SNP",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not name.strip() or not city.strip():
            st.error("Name and City are required.")
        elif not is_edit and not sid.strip():
            st.error("SNP ID is required.")
        elif not is_edit and fetch_snp_by_id(driver, sid.strip()):
            st.error(
                f"SNP ID **{sid.strip()}** already exists. "
                "Each SNP must have a unique ID. "
                "Use the table to edit the existing record."
            )
        else:
            save_snp(
                driver,
                snp_id=sid.strip() if sid else snp_id,
                name=name.strip(),
                city=city.strip(),
                rating=round(rating / 100, 4),
                capacity=int(capacity),
                lat=lat if lat else None,
                lon=lon if lon else None,
                certifications=[c.strip() for c in certs_text.split(",") if c.strip()],
                export_capable=export_capable,
                languages=[l.strip() for l in langs_text.split(",") if l.strip()],
                payment_terms=payment,
                specialization=specialization.strip(),
                category_codes=selected_cats,
            )
            st.success("SNP saved successfully!")
            st.rerun()

    # ── Delete zone (edit only) ───────────────────────────────────────────────
    if is_edit:
        st.markdown('<div class="snpf-sec">Danger Zone</div>', unsafe_allow_html=True)
        st.markdown('<div class="del-zone">', unsafe_allow_html=True)
        confirm = st.checkbox(
            f"I understand this will permanently delete **{existing.get('name', snp_id)}** and all its relationships."
        )
        if st.button(
            "🗑  Delete SNP",
            disabled=not confirm,
            use_container_width=True,
        ):
            delete_snp(driver, snp_id)
            st.success("SNP deleted.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ── Main table ────────────────────────────────────────────────────────────────
try:
    # Add New SNP button
    hdr_col, btn_col = st.columns([5, 1])
    with btn_col:
        if st.button("➕ Add New SNP", use_container_width=True):
            st.session_state["snp_show_add"] = True
            st.rerun()

    snps = fetch_snps_detailed(driver, limit=None)

    if not snps:
        st.info("No SNPs found. Click 'Add New SNP' or run seed_graph.py.")
    else:
        rows = []
        for s in snps:
            cats = s.get("category_codes") or []
            cat_disp = ", ".join(cats[:3]) + (f" +{len(cats)-3}" if len(cats) > 3 else "")
            rows.append({
                "ID": s["id"],
                "Name": s["name"],
                "City": s["city"],
                "Rating": f"{(s['rating'] or 0)*100:.0f}%",
                "Capacity": s["capacity"],
                "Export": "✅" if s.get("export_capable") else "❌",
                "Certifications": len(s.get("certifications") or []),
                "Categories": cat_disp,
                "Payment": s.get("payment_terms") or "—",
            })
        display_df = pd.DataFrame(rows)

        st.caption(
            f"**{len(display_df)} SNPs** — click a row to edit · "
            "double-click a cell to expand text"
        )

        gen = st.session_state.get("snp_df_gen", 0)
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(400, 40 + len(display_df) * 35),
            on_select="rerun",
            selection_mode="single-row",
            key=f"snp_df_{gen}",
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "City": st.column_config.TextColumn("City", width="small"),
                "Rating": st.column_config.TextColumn("Rating", width="small"),
                "Capacity": st.column_config.NumberColumn("Capacity", width="small"),
                "Export": st.column_config.TextColumn("Export", width="small"),
                "Certifications": st.column_config.NumberColumn("Certs #", width="small"),
                "Categories": st.column_config.TextColumn("Categories", width="large"),
                "Payment": st.column_config.TextColumn("Payment", width="small"),
            },
        )

        sel = event.selection.rows
        if sel:
            st.session_state["snp_pending_id"] = display_df.iloc[sel[0]]["ID"]
            st.session_state["snp_df_gen"] = gen + 1
            st.rerun()

    # Phase 2: open the correct dialog
    pending_id = st.session_state.pop("snp_pending_id", None)
    show_add = st.session_state.pop("snp_show_add", False)

    if pending_id:
        @st.dialog(f"Edit SNP — {pending_id}", width="large")
        def _edit_dlg():
            _snp_form(snp_id=pending_id)
        _edit_dlg()

    elif show_add:
        @st.dialog("Add New SNP", width="large")
        def _add_dlg():
            _snp_form(snp_id=None)
        _add_dlg()

except Exception as e:
    st.error(f"Error: {e}")

render_footer()

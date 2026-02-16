import json
import pandas as pd
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.graph_service import (
    fetch_categories,
    fetch_mse_by_id,
    fetch_recent_mses,
    fetch_snps,
    fetch_stats,
)
from msme_app.ui import (
    apply_styles,
    configure_page,
    render_dashboard_header,
    render_footer,
    render_header,
    render_hero,
    render_metrics,
)

config = load_config()
driver = get_driver(config)

configure_page()
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
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🧾 Add MSE", use_container_width=True):
        st.switch_page("pages/01_Add_MSE.py")
render_dashboard_header()

try:
    stats = fetch_stats(driver)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MSEs", stats["mse_count"])
    col2.metric("SNPs", stats["snp_count"])
    col3.metric("Categories", stats["categories"])
    col4.metric("Avg SLA", f"{stats['avg_sla']:.0f}%")

    st.markdown("#### Live Graph Inventory")
    tab1, tab2, tab3 = st.tabs(["MSEs", "SNPs", "Categories"])
    with tab1:
        mses = fetch_recent_mses(driver, limit=20)
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
            st.markdown("#### Recent MSEs")

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

                products_text = _comma(mse_details.get("products"))
                unit_names_text = _comma(mse_details.get("unit_names"))
                nic_codes_text = _comma(mse_details.get("nic_5_digit_codes"))
                category_label = f"{mse_details.get('category_name', '')} ({mse_details.get('category_code', '')})".strip()

                st.markdown(f"**Business:** {mse_details.get('name','')}")
                st.markdown(f"**City:** {mse_details.get('city','')}")
                st.markdown(f"**Udyam:** {mse_details.get('urn','')}")
                st.markdown(f"**Category:** {category_label}")
                st.markdown(f"**Products:** {products_text}")
                st.markdown(f"**Mobile:** {mse_details.get('mobile','')}")
                st.markdown(f"**Email:** {mse_details.get('email','')}")
                st.markdown(f"**Type:** {mse_details.get('type','')}")
                st.markdown(f"**Activity:** {mse_details.get('activity','')}")
                st.markdown(f"**NIC Activity:** {mse_details.get('nic_activity','')}")
                st.markdown(f"**NIC Codes:** {nic_codes_text}")
                st.markdown(f"**Unit Names:** {unit_names_text}")
                address = mse_details.get("address")
                if isinstance(address, dict):
                    st.markdown("**Address:**")
                    st.write(address)
                elif isinstance(address, str):
                    st.markdown(f"**Address:** {address}")

            display_rows = []
            for row in mses_df.fillna("").to_dict(orient="records"):
                category_label = ""
                if row.get("category_name") or row.get("category_code"):
                    category_label = f"{row.get('category_name', '')} ({row.get('category_code', '')})".strip()
                products_val = row.get("products", "")
                if isinstance(products_val, list):
                    products_val = ", ".join([str(v) for v in products_val if v is not None])
                display_rows.append(
                    {
                        "ID": row.get("id", ""),
                        "Business": row.get("name", ""),
                        "City": row.get("city", ""),
                        "Category": category_label,
                        "Products": products_val,
                    }
                )

            display_df = pd.DataFrame(display_rows)
            display_df.insert(0, "Select", False)

            st.markdown(
                """
                <style>
                [data-testid="stDataFrame"] input[type="checkbox"] { border-radius: 999px; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            edited = st.data_editor(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=320,
                column_config={
                    "Select": st.column_config.CheckboxColumn(required=False)
                },
                disabled=[c for c in display_df.columns if c != "Select"],
                key="dash_mse_editor",
            )

            selected_rows = edited[edited["Select"] == True]
            if len(selected_rows) > 1:
                prev_id = st.session_state.get("dash_mse_selected_id")
                selected_ids = selected_rows["ID"].tolist()
                # Prefer the newly selected row if possible
                new_ids = [i for i in selected_ids if i != prev_id]
                keep_id = new_ids[0] if new_ids else selected_ids[0]
                edited["Select"] = False
                edited.loc[edited["ID"] == keep_id, "Select"] = True
                st.session_state["dash_mse_editor"] = edited
                st.session_state["dash_mse_selected_id"] = keep_id
                st.rerun()

            if not selected_rows.empty:
                selected_id = selected_rows.iloc[0]["ID"]
                st.session_state["dash_mse_selected_id"] = selected_id
                if hasattr(st, "dialog"):
                    @st.dialog("MSE Details")
                    def _dialog(mse_id):
                        render_mse_details(mse_id)
                    _dialog(selected_id)
                else:
                    with st.expander("MSE Details", expanded=True):
                        render_mse_details(selected_id)
    with tab2:

        snps = fetch_snps(driver, limit=None)
        snps_df = pd.DataFrame(
            snps, columns=["ID", "Name", "City", "Rating", "Capacity"]
        )
        if snps_df.empty:
            st.info("No SNPs found. Run seed_graph.py to populate SNPs.")
        else:
            st.dataframe(snps_df, use_container_width=True, hide_index=True)
    with tab3:
        cats = fetch_categories(driver, limit=None)
        cats_df = pd.DataFrame(cats, columns=["Code", "Name", "Sector", "Keywords"])
        if cats_df.empty:
            st.info("No categories found. Run seed_graph.py to populate categories.")
        else:
            st.dataframe(cats_df, use_container_width=True, hide_index=True)

except Exception:
    st.info("Run Setup -> Add MSE -> See live graph analytics!")

render_footer()

import json
import pandas as pd
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
    # Fetch enhanced analytics
    analytics = fetch_analytics_summary(driver)
    
    # Enhanced metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MSEs", analytics["total_mses"])
    col2.metric("SNPs", analytics["total_snps"])
    col3.metric("Categories", analytics["total_categories"])
    col4.metric("Avg Rating", f"{analytics['avg_rating']*100:.0f}%")
    
    # Secondary metrics row
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Capacity", f"{analytics['total_capacity']:,}")
    col6.metric("Export-Ready SNPs", analytics["export_capable_snps"])
    col7.metric("Cities Covered", analytics["unique_cities"])
    col8.metric("Active Connections", analytics["total_relationships"])

    st.markdown("#### Live Graph Inventory")
    tab1, tab2, tab3 = st.tabs(["MSEs", "SNPs 🆕", "Categories 🆕"])
    
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
        st.markdown("#### Enhanced SNP View with Rich Metadata")
        
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
            
            st.markdown(f"**Showing {len(filtered_df)} of {len(snps_df)} SNPs**")
            
            # Display table
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
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
        st.markdown("#### Enhanced Category View with ONDC Mapping")
        
        # Fetch detailed category data
        cats = fetch_categories_detailed(driver, limit=None)
        
        if not cats:
            st.info("No categories found. Run seed_graph.py to populate categories.")
        else:
            # Create display dataframe
            cat_rows = []
            for cat in cats:
                # Format keywords
                keywords = cat.get("keywords") or []
                keyword_display = ", ".join(keywords[:5]) if keywords else "None"
                if len(keywords) > 5:
                    keyword_display += f" +{len(keywords)-5}"
                
                # Format ONDC path
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
            
            # Add filters
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                sector_filter = st.selectbox(
                    "Filter by Sector",
                    ["All"] + sorted(cats_df["Sector"].unique().tolist()),
                    key="cat_sector_filter"
                )
            with col_c2:
                has_snps = st.checkbox(
                    "Only categories with SNPs",
                    value=False,
                    key="cat_has_snps_filter"
                )
            
            # Apply filters
            filtered_cats = cats_df.copy()
            if sector_filter != "All":
                filtered_cats = filtered_cats[filtered_cats["Sector"] == sector_filter]
            if has_snps:
                filtered_cats = filtered_cats[filtered_cats["SNPs"] > 0]
            
            st.markdown(f"**Showing {len(filtered_cats)} of {len(cats_df)} Categories**")
            
            # Display table
            st.dataframe(
                filtered_cats,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Code": st.column_config.TextColumn("Code", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Sector": st.column_config.TextColumn("Sector", width="small"),
                    "SNPs": st.column_config.NumberColumn("SNPs", width="small"),
                    "Keywords (Sample)": st.column_config.TextColumn("Keywords", width="large"),
                    "ONDC Taxonomy": st.column_config.TextColumn("ONDC Path", width="large"),
                }
            )
            
            # Category insights
            with st.expander("📈 Category Insights", expanded=False):
                st.markdown("**Coverage Analysis:**")
                coverage_summary = cats_df.groupby("Sector")["SNPs"].agg(["sum", "mean", "count"])
                coverage_summary.columns = ["Total SNPs", "Avg SNPs/Category", "Categories"]
                st.dataframe(coverage_summary, use_container_width=True)

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Run seed_graph.py to populate the database, then restart the app.")

render_footer()

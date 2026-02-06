import tempfile
from datetime import datetime

import pandas as pd
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.categorization import categorize_products
from msme_app.services.graph_service import (
    fetch_categories,
    fetch_cities,
    fetch_recent_mses,
    fetch_snps,
    fetch_stats,
    run_reasoning,
    save_mse,
    setup_knowledge_graph,
)
from msme_app.services.nlp_service import extract_entities, normalize_city
from msme_app.services.whisper_service import load_whisper_model, transcribe_audio
from msme_app.ui import (
    apply_styles,
    configure_page,
    render_dashboard_header,
    render_footer,
    render_graph_header,
    render_header,
    render_hero,
    render_metrics,
    render_reasoning_cards,
)


config = load_config()
driver = get_driver(config)

configure_page()
apply_styles()
render_header()
render_hero()
render_metrics()
st.markdown("---")

st.subheader("Voice-First Onboarding")
st.caption("Upload a voice sample or enter details manually.")

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "form_data" not in st.session_state:
    st.session_state.form_data = None
if "toast_message" not in st.session_state:
    st.session_state.toast_message = None

model = load_whisper_model()

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

city_list = fetch_cities(driver)
categories = fetch_categories(driver, limit=None)
category_options = [f"{row['name']} ({row['code']})" for row in categories]
category_map = {opt: opt.split("(")[-1].strip(")") for opt in category_options}
category_name_map = {row["code"]: row["name"] for row in categories}

tab_voice, tab_manual = st.tabs(["Voice Assisted", "Manual Entry"])

with tab_voice:
    st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
    language_choice = st.selectbox(
        "Speech Language",
        ["Auto Detect", "Hindi", "English"],
        index=0,
        key="voice_language",
    )
    uploaded_file = st.file_uploader(
        "Hindi/English Voice",
        type=["wav", "mp3", "m4a"],
        key=f"voice_uploader_{st.session_state.uploader_key}",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        st.audio(uploaded_file)
        if st.session_state.form_data is None:
            with st.spinner("Transcribing and extracting details"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                language_map = {
                    "Auto Detect": "auto",
                    "Hindi": "hi",
                    "English": "en",
                }
                transcription = transcribe_audio(
                    model, tmp_path, language=language_map.get(language_choice)
                )
                entities = extract_entities(transcription)
                entities["city"] = normalize_city(
                    entities.get("city", ""), transcription, city_list
                )
                if not entities.get("business_name"):
                    products = entities.get("products") or []
                    if products:
                        entities["business_name"] = " & ".join(products[:2]).title()
                    else:
                        entities["business_name"] = "Unnamed MSE"
                category_code, category_name = categorize_products(
                    entities["products"],
                    driver,
                    business_name=entities.get("business_name", ""),
                    transcription=transcription,
                )
                st.session_state.form_data = {
                    "transcription": transcription,
                    "business_name": entities["business_name"],
                    "city": entities.get("city", ""),
                    "products": ", ".join(entities.get("products") or []),
                    "category_code": category_code,
                    "category_name": category_name,
                }
    if st.session_state.form_data:
        st.markdown("#### Confirm Details")
        business_name = st.text_input(
            "Business Name",
            value=st.session_state.form_data.get("business_name", ""),
            key="voice_business",
        )
        city = st.selectbox(
            "City",
            options=city_list,
            index=city_list.index(st.session_state.form_data.get("city"))
            if st.session_state.form_data.get("city") in city_list
            else 0,
            key="voice_city",
        )
        products_text = st.text_input(
            "Products (comma-separated)",
            value=st.session_state.form_data.get("products", ""),
            key="voice_products",
        )
        category_default = (
            f"{st.session_state.form_data['category_name']} "
            f"({st.session_state.form_data['category_code']})"
        )
        category_selection = st.selectbox(
            "Category",
            options=category_options,
            index=category_options.index(category_default)
            if category_default in category_options
            else 0,
            key="voice_category",
        )
        save_clicked = st.button("Save MSE", type="primary", key="voice_save")
        if save_clicked:
            category_code = category_map.get(category_selection, "TX001")
            category_name = category_name_map.get(category_code, "Textiles")
            products = [p.strip() for p in products_text.split(",") if p.strip()]
            mse_id = f"MSE{datetime.now().strftime('%H%M%S')}"
            save_mse(driver, mse_id, business_name, city, products, category_code)
            reasoning_result = run_reasoning(driver, mse_id, city)
            st.session_state.last_result = {
                "transcription": st.session_state.form_data.get("transcription", ""),
                "entities": {"business_name": business_name, "city": city},
                "category_code": category_code,
                "category_name": category_name,
                "mse_id": mse_id,
                "reasoning_result": reasoning_result,
            }
            st.session_state.toast_message = f"MSE {mse_id} created and mapped."
            st.session_state.uploader_key += 1
            st.session_state.form_data = None
            st.rerun()

with tab_manual:
    st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
    manual_business = st.text_input(
        "Business Name", value="", key="manual_business"
    )
    manual_city = st.selectbox("City", options=city_list, key="manual_city")
    manual_products = st.text_input(
        "Products (comma-separated)", value="", key="manual_products"
    )
    manual_category = st.selectbox(
        "Category", options=category_options, key="manual_category"
    )
    manual_save = st.button("Save MSE", type="primary", key="manual_save")
    st.markdown("</div>", unsafe_allow_html=True)
    if manual_save:
        category_code = category_map.get(manual_category, "TX001")
        category_name = category_name_map.get(category_code, "Textiles")
        products = [p.strip() for p in manual_products.split(",") if p.strip()]
        mse_id = f"MSE{datetime.now().strftime('%H%M%S')}"
        save_mse(
            driver,
            mse_id,
            manual_business or "Unnamed MSE",
            manual_city,
            products,
            category_code,
        )
        reasoning_result = run_reasoning(driver, mse_id, manual_city)
        st.session_state.last_result = {
            "transcription": "",
            "entities": {
                "business_name": manual_business or "Unnamed MSE",
                "city": manual_city,
            },
            "category_code": category_code,
            "category_name": category_name,
            "mse_id": mse_id,
            "reasoning_result": reasoning_result,
        }
        st.session_state.toast_message = f"MSE {mse_id} created and mapped."
        for key in [
            "manual_business",
            "manual_city",
            "manual_products",
            "manual_category",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.form_data = None
        st.rerun()

if st.session_state.last_result:
    result = st.session_state.last_result

    col1, col2, col3 = st.columns(3)
    col1.metric("Business", result["entities"]["business_name"])
    col2.metric("City", result["entities"]["city"])
    col3.metric(
        "Category", f"{result['category_name']} ({result['category_code']})"
    )

    status_message = st.session_state.toast_message or f"MSE {result['mse_id']} created and mapped."
    st.success(status_message)
    st.session_state.toast_message = None
    st.markdown("---")
    render_graph_header()
    render_reasoning_cards(
        result["reasoning_result"],
        result["entities"]["city"],
        result["category_name"],
        result["category_code"],
    )

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
        mses = fetch_recent_mses(driver, limit=10)
        mses_df = pd.DataFrame(mses, columns=["ID", "Name", "City", "Products"])
        if mses_df.empty:
            st.info("No MSEs yet. Upload voice and process to create MSEs.")
        else:
            st.dataframe(mses_df, use_container_width=True, hide_index=True)
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
    st.info("Run Setup -> Upload voice -> See live graph analytics!")

render_footer()

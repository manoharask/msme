import json
import os
import tempfile
from datetime import datetime

import pandas as pd
import streamlit as st

from msme_app.config import get_driver, load_config
from msme_app.services.categorization import categorize_products
from msme_app.services.graph_service import (
    fetch_categories,
    fetch_cities,
    fetch_mse_by_id,
    fetch_recent_mses,
    fetch_snps,
    fetch_stats,
    run_reasoning,
    save_mse,
)
from msme_app.services.nlp_service import extract_entities, normalize_city
from msme_app.services.ocr_service import (
    process_udyam_certificate,
    process_with_fallback,
)
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

@st.cache_resource
def _get_driver():
    return get_driver(load_config())

driver = _get_driver()

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
st.markdown("---")

st.subheader("Voice-First Onboarding")
st.caption("Upload a voice sample or enter details manually.")

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "udyam_uploader_key" not in st.session_state:
    st.session_state.udyam_uploader_key = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "toast_message" not in st.session_state:
    st.session_state.toast_message = None
if "form_data_voice" not in st.session_state:
    st.session_state.form_data_voice = None
if "form_data_manual" not in st.session_state:
    st.session_state.form_data_manual = None
if "form_data_udyam" not in st.session_state:
    st.session_state.form_data_udyam = None
# Guard so manual tab doesn't reinitialize its form on every rerun
if "manual_initialized" not in st.session_state:
    st.session_state.manual_initialized = False

model = load_whisper_model()

city_list = fetch_cities(driver)
categories = fetch_categories(driver, limit=None)
category_options = [f"{row['name']} ({row['code']})" for row in categories]
category_map = {opt: opt.split("(")[-1].strip(")") for opt in category_options}
category_name_map = {row["code"]: row["name"] for row in categories}

tab_voice, tab_manual, tab_udyam = st.tabs(
    ["Voice Assisted", "Manual Entry", "Udyam Certificate"]
)


def reset_form_keys(prefix):
    keys = [k for k in st.session_state.keys() if k.startswith(f"{prefix}_")]
    for k in keys:
        del st.session_state[k]


def render_confirm_form(form_key_prefix):
    data_key = f"form_data_{form_key_prefix}"
    data = st.session_state.get(data_key)
    if not data:
        return

    local_city_list = list(city_list)
    data_city = (data.get("city") or "").strip()
    if data_city and data_city not in local_city_list:
        local_city_list = [data_city] + local_city_list

    local_category_options = category_options
    local_category_map = category_map
    local_category_name_map = category_name_map
    data_category_code = data.get("category_code")
    data_category_name = data.get("category_name")
    if data_category_code and data_category_name:
        option_label = f"{data_category_name} ({data_category_code})"
        if option_label not in local_category_options:
            local_category_options = [option_label] + local_category_options
            local_category_map = dict(local_category_map)
            local_category_name_map = dict(local_category_name_map)
            local_category_map[option_label] = data_category_code
            local_category_name_map[data_category_code] = data_category_name

    def _comma_list(value):
        if isinstance(value, list):
            return ", ".join([str(v) for v in value if v is not None])
        return value or ""

    st.markdown(
        '''<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        <div style="width:4px;height:28px;background:linear-gradient(180deg,#2563eb,#7c3aed);border-radius:4px;flex-shrink:0;"></div>
        <div>
          <div style="font-size:1.05rem;font-weight:700;color:#0f172a;letter-spacing:-0.01em;">MSE Onboarding</div>
          <div style="font-size:0.72rem;color:#64748b;margin-top:1px;">Review and confirm details extracted from your input</div>
        </div></div>''', unsafe_allow_html=True)

    st.markdown('<div class="fsec fsec-blue"><span class="fsec-icon">🏷️</span>Business Identity</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    business_name = col1.text_input(
        "Business Name",
        value=data.get("business_name", ""),
        key=f"{form_key_prefix}_business",
    )
    city = col2.selectbox(
        "City",
        options=local_city_list,
        index=local_city_list.index(data.get("city"))
        if data.get("city") in local_city_list
        else 0,
        key=f"{form_key_prefix}_city",
    )

    col1, col2 = st.columns(2)
    products_text = col1.text_input(
        "Products (comma-separated)",
        value=_comma_list(data.get("products", "")),
        key=f"{form_key_prefix}_products",
    )
    category_default = (
        f"{data.get('category_name', 'Textiles')} "
        f"({data.get('category_code', 'TX001')})"
    )
    category_selection = col2.selectbox(
        "Category",
        options=local_category_options,
        index=local_category_options.index(category_default)
        if category_default in local_category_options
        else 0,
        key=f"{form_key_prefix}_category",
    )


    st.markdown('<div class="fsec fsec-green"><span class="fsec-icon">📋</span>Registration &amp; Contact</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    urn = col1.text_input(
        "Udyam Registration Number",
        value=data.get("urn", ""),
        key=f"{form_key_prefix}_urn",
    )
    mobile = col2.text_input(
        "Mobile",
        value=data.get("mobile", ""),
        key=f"{form_key_prefix}_mobile",
    )

    col1, col2 = st.columns(2)
    email = col1.text_input(
        "Email",
        value=data.get("email", ""),
        key=f"{form_key_prefix}_email",
    )
    enterprise_type = col2.text_input(
        "Type of Enterprise",
        value=data.get("type", ""),
        key=f"{form_key_prefix}_type",
    )


    st.markdown('<div class="fsec fsec-violet"><span class="fsec-icon">🏭</span>Enterprise Classification</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    activity = col1.text_input(
        "Activity",
        value=data.get("activity", ""),
        key=f"{form_key_prefix}_activity",
    )
    social_category = col2.text_input(
        "Social Category",
        value=data.get("social_category", ""),
        key=f"{form_key_prefix}_social",
    )


    st.markdown('<div class="fsec fsec-amber"><span class="fsec-icon">📅</span>Key Dates</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    incorporation_date = col1.text_input(
        "Incorporation Date",
        value=data.get("incorporation_date", ""),
        key=f"{form_key_prefix}_incorp",
    )
    commencement_date = col2.text_input(
        "Commencement Date",
        value=data.get("commencement_date", ""),
        key=f"{form_key_prefix}_commence",
    )

    col1, col2 = st.columns(2)
    registration_date = col1.text_input(
        "Registration Date",
        value=data.get("registration_date", ""),
        key=f"{form_key_prefix}_register",
    )
    state = col2.text_input(
        "State",
        value=data.get("state", ""),
        key=f"{form_key_prefix}_state",
    )

    col1, col2 = st.columns(2)
    pin = col1.text_input(
        "PIN",
        value=data.get("pin", ""),
        key=f"{form_key_prefix}_pin",
    )
    nic_activity = col2.text_input(
        "NIC Activity",
        value=data.get("nic_activity", ""),
        key=f"{form_key_prefix}_nic_activity",
    )

    col1, col2 = st.columns(2)
    nic_codes_text = col1.text_input(
        "NIC 5 Digit Codes (comma-separated)",
        value=_comma_list(data.get("nic_5_digit_codes", "")),
        key=f"{form_key_prefix}_nic_codes",
    )
    unit_names_text = col2.text_input(
        "Unit Names (comma-separated)",
        value=_comma_list(data.get("unit_names", "")),
        key=f"{form_key_prefix}_unit_names",
    )

    address = data.get("address") or {}
    if isinstance(address, str) and address.strip():
        try:
            address = json.loads(address)
        except json.JSONDecodeError:
            address = {}


    st.markdown('<div class="fsec fsec-rose"><span class="fsec-icon">📍</span>Registered Address</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    flat = col1.text_input(
        "Flat/Door/Block",
        value=address.get("flat", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_flat",
    )
    premises = col2.text_input(
        "Premises/Building",
        value=address.get("premises", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_premises",
    )

    col1, col2 = st.columns(2)
    road = col1.text_input(
        "Road/Street/Lane",
        value=address.get("road", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_road",
    )
    village = col2.text_input(
        "Village/Town",
        value=address.get("village", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_village",
    )

    col1, col2 = st.columns(2)
    block = col1.text_input(
        "Block",
        value=address.get("block", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_block",
    )
    district = col2.text_input(
        "District",
        value=address.get("district", "") if isinstance(address, dict) else "",
        key=f"{form_key_prefix}_addr_district",
    )


    save_clicked = st.button(
        "💾  Save & Match SNPs", type="primary", key=f"{form_key_prefix}_save"
    )
    if save_clicked:
        category_code = local_category_map.get(category_selection, "TX001")
        category_name = local_category_name_map.get(category_code, "Textiles")
        products = [p.strip() for p in products_text.split(",") if p.strip()]

        # ── Auto-categorize from products when user hasn't manually changed
        # the category (it stayed at the default TX001 for manual entry)
        if products and category_code == "TX001" and form_key_prefix == "manual":
            auto_code, auto_name = categorize_products(
                products, driver, business_name=business_name
            )
            if auto_code != "TX001":
                category_code = auto_code
                category_name = auto_name

        nic_codes = [c.strip() for c in nic_codes_text.split(",") if c.strip()]
        unit_names = [u.strip() for u in unit_names_text.split(",") if u.strip()]
        address_dict = {
            k: v
            for k, v in {
                "flat": flat,
                "premises": premises,
                "road": road,
                "village": village,
                "block": block,
                "district": district,
                "city": city,
                "state": state,
                "pin": pin,
            }.items()
            if v
        }
        # Use microseconds to avoid ID collision when saving quickly
        mse_id = f"MSE{datetime.now().strftime('%H%M%S%f')[:11]}"
        save_mse(
            driver,
            mse_id,
            business_name,
            city,
            products,
            category_code,
            category_name=category_name,
            urn=urn,
            mobile=mobile,
            email=email,
            enterprise_type=enterprise_type,
            activity=activity,
            social_category=social_category,
            incorporation_date=incorporation_date,
            commencement_date=commencement_date,
            registration_date=registration_date,
            address=address_dict or None,
            state=state,
            pin=pin,
            unit_names=unit_names or None,
            nic_5_digit_codes=nic_codes or None,
            nic_activity=nic_activity,
            source=data.get("source"),
        )
        reasoning_result = run_reasoning(driver, mse_id, city)
        st.session_state.last_result = {
            "transcription": data.get("transcription", ""),
            "source": data.get("source", ""),          # identifies which tab owns this result
            "entities": {"business_name": business_name, "city": city},
            "category_code": category_code,
            "category_name": category_name,
            "mse_id": mse_id,
            "reasoning_result": reasoning_result,
        }
        st.session_state.toast_message = f"MSE {mse_id} created and mapped."
        if data.get("source") == "voice":
            st.session_state.uploader_key += 1
        if data.get("source") == "udyam":
            st.session_state.udyam_uploader_key += 1
        st.session_state[data_key] = None
        st.rerun()

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

    if uploaded_file is not None:
        st.audio(uploaded_file)
        if st.session_state.get("form_data_voice") is None:
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
                st.session_state.last_result = None
                st.session_state.toast_message = None
                reset_form_keys("voice")
                st.session_state.form_data_voice = {
                    "source": "voice",
                    "transcription": transcription,
                    "business_name": entities["business_name"],
                    "city": entities.get("city", ""),
                    "products": ", ".join(entities.get("products") or []),
                    "category_code": category_code,
                    "category_name": category_name,
                    "urn": "",
                    "mobile": "",
                    "email": "",
                    "type": "",
                    "activity": "",
                    "social_category": "",
                    "incorporation_date": "",
                    "commencement_date": "",
                    "registration_date": "",
                    "address": {},
                    "state": "",
                    "pin": "",
                    "unit_names": "",
                    "nic_5_digit_codes": "",
                    "nic_activity": "",
                }
    render_confirm_form("voice")


with tab_manual:
    # Only initialize the blank form on first load, NOT on every rerun.
    # Bug: after Save+rerun, form_data_manual was None so it re-initialized
    # to a blank dict, render_confirm_form rendered a fresh empty form, and
    # the SNP cards below the tabs were hidden under it.
    if not st.session_state.manual_initialized:
        st.session_state.last_result = None
        st.session_state.toast_message = None
        st.session_state.form_data_manual = {
            "source": "manual",
            "transcription": "",
            "business_name": "",
            "city": "",
            "products": "",
            "category_code": "TX001",
            "category_name": "Textiles",
            "urn": "",
            "mobile": "",
            "email": "",
            "type": "",
            "activity": "",
            "social_category": "",
            "incorporation_date": "",
            "commencement_date": "",
            "registration_date": "",
            "address": {},
            "state": "",
            "pin": "",
            "unit_names": "",
            "nic_5_digit_codes": "",
            "nic_activity": "",
        }
        st.session_state.manual_initialized = True

    st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)

    # If we just saved and have a result, show it inside this tab
    if st.session_state.last_result and st.session_state.last_result.get("source") == "manual":
        result = st.session_state.last_result
        col1, col2, col3 = st.columns(3)
        col1.metric("Business", result["entities"]["business_name"])
        col2.metric("City",     result["entities"]["city"])
        col3.metric("Category", f"{result['category_name']} ({result['category_code']})")
        status_msg = st.session_state.toast_message or f"MSE {result['mse_id']} created and mapped."
        st.success(status_msg)
        st.session_state.toast_message = None
        st.markdown("---")
        render_graph_header()
        if result.get("reasoning_result"):
            render_reasoning_cards(
                result["reasoning_result"],
                result["entities"]["city"],
                result["category_name"],
                result["category_code"],
            )
        else:
            st.warning(
                f"\u26a0\ufe0f No SNP matches found for "
                f"**{result['category_name']} ({result['category_code']})** "
                f"in **{result['entities']['city']}**. "
                "Check that seed_graph.py has been run and SNPs cover this category."
            )
        if st.button("Add Another MSE", key="manual_add_another"):
            st.session_state.last_result = None
            st.session_state.manual_initialized = False
            st.session_state.form_data_manual = None
            st.rerun()
    else:
        render_confirm_form("manual")

with tab_udyam:
    st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
    st.markdown("#### Or Upload Udyam Certificate")
    use_llm_fallback = st.checkbox(
        "Use LLM fallback if OCR fails",
        value=False,
        key="udyam_llm_fallback",
    )
    udyam_file = st.file_uploader(
        "Upload Udyam Certificate (PDF/Image)",
        type=["pdf", "png", "jpg", "jpeg"],
        key=f"udyam_uploader_{st.session_state.udyam_uploader_key}",
    )

    if udyam_file is not None:
        st.session_state.last_result = None
        st.session_state.toast_message = None
        with st.spinner("Processing Udyam certificate..."):
            suffix = os.path.splitext(udyam_file.name)[1] or ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(udyam_file.read())
                tmp_path = tmp.name

            if use_llm_fallback:
                certificate_data = process_with_fallback(tmp_path)
            else:
                certificate_data = process_udyam_certificate(tmp_path)

        if certificate_data.get("error"):
            st.error(f"OCR failed: {certificate_data['error']}")
        else:
            urn = certificate_data.get("urn")
            if urn:
                st.success(f"Certificate extracted: {urn}")
                validation = certificate_data.get("urn_validation")
                if validation and not validation.get("valid"):
                    st.warning("Extracted URN looks invalid. Please verify.")
            else:
                st.warning("Could not extract Udyam number. Please verify certificate quality.")

            business_name = certificate_data.get("business_name") or "Unnamed MSE"
            city = normalize_city(
                certificate_data.get("city", ""), "", city_list
            )
            nic_activity = certificate_data.get("nic_activity")
            nic_codes = certificate_data.get("nic_5_digit_codes") or []
            if nic_activity and nic_codes:
                category_code = f"NIC{nic_codes[0]}"
                category_name = nic_activity
            else:
                category_code, category_name = categorize_products(
                    [],
                    driver,
                    business_name=business_name,
                    transcription="",
                )
            products = nic_activity or ""
            st.session_state.form_data_udyam = {
                "source": "udyam",
                "transcription": "",
                "business_name": business_name,
                "city": city,
                "products": products,
                "category_code": category_code,
                "category_name": category_name,
                "urn": urn,
                "mobile": certificate_data.get("mobile"),
                "email": certificate_data.get("email"),
                "type": certificate_data.get("type"),
                "activity": certificate_data.get("activity"),
                "social_category": certificate_data.get("social_category"),
                "incorporation_date": certificate_data.get("incorporation_date"),
                "commencement_date": certificate_data.get("commencement_date"),
                "registration_date": certificate_data.get("registration_date"),
                "address": certificate_data.get("address"),
                "state": certificate_data.get("state"),
                "pin": certificate_data.get("pin"),
                "unit_names": certificate_data.get("unit_names"),
                "nic_5_digit_codes": certificate_data.get("nic_5_digit_codes"),
                "nic_activity": nic_activity,
            }

    render_confirm_form("udyam")


# Show SNP matching results for voice and udyam tabs (manual shows inside its own tab)
if st.session_state.last_result and st.session_state.last_result.get("source") != "manual":
    result = st.session_state.last_result

    col1, col2, col3 = st.columns(3)
    col1.metric("Business", result["entities"]["business_name"])
    col2.metric("City",     result["entities"]["city"])
    col3.metric("Category", f"{result['category_name']} ({result['category_code']})")

    status_message = st.session_state.toast_message or f"MSE {result['mse_id']} created and mapped."
    st.success(status_message)
    st.session_state.toast_message = None
    st.markdown("---")
    render_graph_header()
    if result.get("reasoning_result"):
        render_reasoning_cards(
            result["reasoning_result"],
            result["entities"]["city"],
            result["category_name"],
            result["category_code"],
        )
    else:
        st.warning(
            f"\u26a0\ufe0f No SNP matches found for "
            f"**{result['category_name']} ({result['category_code']})** "
            f"in **{result['entities']['city']}**. "
            "Check that seed_graph.py has been run and SNPs cover this category."
        )

render_footer()

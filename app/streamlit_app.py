import datetime as dt

import streamlit as st
from src.config import get_config, configure_logging
from src.hunt_generator import HuntGenerator
from src.ollama_client import ModelJSONError

st.set_page_config(page_title="Kagaz — Offline Nature Hunt",
                   page_icon="🍂", layout="centered")

st.title("🍂 Kagaz — Offline Nature Hunt")
st.caption("Runs fully offline on Gemma via Ollama. Nothing leaves your laptop.")

st.sidebar.header("Settings")
age = st.selectbox("Age group", ["4-6", "6-8", "8-10", "10-12"])
city = st.text_input("City", "Pune")
month = st.selectbox("Month", ["January", "February", "March", "April",
                                 "May", "June", "July", "August",
                                 "September", "October", "November", "December"],
                     index=dt.datetime.now().month - 1)
item_count = st.slider("Number of items", 6, 20, 12)
season_hint = st.text_input("Season hint (optional)", "")

from datetime import datetime
get_generator = st.cache_resource(lambda: HuntGenerator(get_config()))

if st.button("Generate"):
    gen = get_generator()
    with st.spinner("Gemma is thinking..."):
        try:
            hunt = gen.generate(age, city, month, item_count, season_hint)
            pdf_path = gen.generate_pdf(hunt, city, month)
        except ModelJSONError as e:
            st.error(f"Model returned invalid JSON: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    st.success("Hunt ready!")
    st.subheader(hunt["title"])
    st.write(hunt["intro"])
    for item in hunt["items"]:
        st.markdown(f"**{item['emoji']} {item['text_hi']}** — {item['text_en']}")
        st.caption(f"_{item['hint']}_")
    st.info(f"🎯 {hunt['bonus_challenge']}")
    st.caption(f"👨‍👩‍👧 {hunt['parent_note']}")
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Download printable PDF", f.read(),
                           file_name=pdf_path.name, mime="application/pdf")
    with st.expander("Raw JSON"):
        st.json(hunt)

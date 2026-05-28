import streamlit as st
import subprocess

st.title("🌍 Global Stock Screener")
code = st.text_input("Entre ton code d'accès :")
if code != "MONCODE123":
    st.warning("Code incorrect. Accès refusé.")
    st.stop()

if st.button("Lancer le scan"):
    with st.spinner("Analyse en cours..."):
        result = subprocess.run(
            ["python3", "/Users/maxou/Desktop/global_screener.py"],
            capture_output=True, text=True
        )
        st.text(result.stdout)

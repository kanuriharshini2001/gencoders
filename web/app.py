# app.py
import streamlit as st
from pathlib import Path
import json
from scripts.run_review import run_pipeline_from_string

st.set_page_config(page_title="AutoCodeFixer", layout="wide")
st.title("AutoCodeFixer — AI Code Reviewer & Refactoring Assistant (Demo)")

st.markdown("Paste Python code in the editor and click **Analyze + Refactor**. Outputs are saved in the `reports/` folder.")

code = st.text_area("Python code", height=300, value="# Paste Python code here\n")

col1, col2 = st.columns([1,1])
with col1:
    if st.button("Analyze + Refactor"):
        if not code.strip():
            st.error("Please paste Python code.")
        else:
            with st.spinner("Running pipeline..."):
                result = run_pipeline_from_string(code)
            st.success("Analysis complete. Results saved to `reports/`.")
            st.json(result)

with col2:
    st.subheader("Last outputs")
    p = Path("reports/last_result.json")
    if p.exists():
        st.json(json.loads(p.read_text()))
    else:
        st.info("No previous run. Run Analyze + Refactor to create outputs.")

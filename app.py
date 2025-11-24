import streamlit as st
from scripts.run_review import run_pipeline_from_string

# 1. Page Configuration
st.set_page_config(
    page_title="GenCoders AI Reviewer",
    page_icon="🤖",
    layout="wide"
)

# 2. CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stTextArea textarea {
        font-family: 'Consolas', 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🤖 GenCoders: AI Code Reviewer & Refactorer")
st.markdown("""
**Automated SDLC Assistant** | Powered by Google Gemini 1.5 Flash
*Paste your Python code below. The Multi-Agent System will detect bugs, refactor logic, and explain the changes.*
""")
st.divider()

# 4. Layout: Left Column (Input) / Right Column (Output)
col_input, col_output = st.columns([1, 1])

with col_input:
    st.subheader("📝 Input Source Code")
    
    # Default example code to help the user test immediately
    default_code = """def calculate_total(price, tax):
    # This has a NameError bug (tax_rate vs tax)
    # And a security issue (hardcoded token)
    api_token = "sk-12345-SECRET-KEY"
    
    total = price + (price * tax_rate)
    return total

print(calculate_total(100, 0.05))"""

    code_input = st.text_area("Python Code", value=default_code, height=500)
    
    run_btn = st.button("🚀 Analyze & Refactor Code", type="primary", use_container_width=True)

# 5. Logic to Run Pipeline
if run_btn:
    if not code_input.strip():
        st.error("Please enter code to analyze.")
    else:
        with st.spinner("🔄 Orchestrating Agents... (Analyzing -> Refactoring -> Explaining)"):
            try:
                # Call the backend script
                results = run_pipeline_from_string(code_input)
                # Save to session state so it persists
                st.session_state['results'] = results
                st.success("Pipeline Execution Successful!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# 6. Output Display (Right Column)
with col_output:
    st.subheader("📊 Analysis Results")
    
    if 'results' in st.session_state:
        res = st.session_state['results']
        
        # Create Tabs
        tab1, tab2, tab3 = st.tabs(["🐞 Bug Report", "✨ Refactored Code", "🎓 AI Explanation"])
        
        # --- TAB 1: BUG REPORT ---
        with tab1:
            issues = res.get("issues", [])
            if not issues:
                st.balloons()
                st.success("✅ No critical issues found! Your code looks clean.")
            else:
                st.write(f"**Found {len(issues)} issues:**")
                for i, issue in enumerate(issues):
                    severity = issue.get('severity', 'Medium')
                    line = issue.get('line', '?')
                    desc = issue.get('issue', 'Unknown issue')
                    
                    # Color code based on severity
                    if severity == "High":
                        st.error(f"🚨 **Line {line} (High):** {desc}")
                    else:
                        st.warning(f"⚠️ **Line {line} ({severity}):** {desc}")

        # --- TAB 2: REFACTORED CODE ---
        with tab2:
            st.markdown("### ✅ Optimized Code")
            st.code(res.get("refactored_code", ""), language="python")

        # --- TAB 3: EXPLANATION ---
        with tab3:
            st.markdown("### 🧠 What changed and why?")
            st.markdown(res.get("explanation", "No explanation generated."))
            
    else:
        st.info("👈 Click 'Analyze' to start the multi-agent pipeline.")
import streamlit as st
from scripts.run_review import run_pipeline_from_string, process_batch_files

# 1. Page Configuration
st.set_page_config(
    page_title="GenCoders AI Reviewer",
    page_icon="🤖",
    layout="wide"
)

# 2. CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTextArea textarea { font-family: 'Consolas', 'Courier New', monospace; }
    .diff-header { font-weight: bold; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 10px; }
    .orig-header { background-color: #ffebee; color: #c62828; }
    .ref-header { background-color: #e8f5e9; color: #2e7d32; }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🤖 GenCoders: AI Code Reviewer & Refactorer")
st.markdown("**Automated SDLC Assistant** | Batch Processing Enabled")
st.divider()

# 4. Input Mode Selection
mode = st.radio("Select Input Mode:", ["📝 Paste Code Snippet", "📂 Upload Folder / Multiple Files"], horizontal=True)

if 'results' not in st.session_state:
    st.session_state['results'] = {}
if 'current_file' not in st.session_state:
    st.session_state['current_file'] = "Single Snippet"

# --- MODE A: PASTE CODE ---
if mode == "📝 Paste Code Snippet":
    default_code = """def crash_me(data):
    # Security Flaw
    key = "sk-12345"
    return data[0]"""
    
    code_input = st.text_area("Paste Python Code:", value=default_code, height=300)
    
    if st.button("🚀 Analyze Snippet", type="primary"):
        with st.spinner("🔄 Orchestrating Agents... (Analyzing -> Refactoring -> Explaining)"):
            res = run_pipeline_from_string(code_input)
            st.session_state['results'] = {"Single Snippet": res}
            st.session_state['current_file'] = "Single Snippet"
            st.success("Analysis Complete!")

# --- MODE B: BATCH UPLOAD ---
else:
    uploaded_files = st.file_uploader("Upload Python files (.py)", type=["py"], accept_multiple_files=True)
    
    if st.button("🚀 Analyze All Files", type="primary"):
        if not uploaded_files:
            st.error("Please upload files first.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results_dict = {}
            total_files = len(uploaded_files)
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Analyzing {file.name} ({i+1}/{total_files})...")
                file.seek(0)
                content = file.read().decode("utf-8")
                results_dict[file.name] = run_pipeline_from_string(content)
                progress_bar.progress((i + 1) / total_files)
            
            st.session_state['results'] = results_dict
            st.session_state['current_file'] = uploaded_files[0].name
            st.success(f"Successfully analyzed {total_files} files!")

st.divider()

# 5. Display Results
results = st.session_state.get('results', {})

if results:
    with st.sidebar:
        st.header("📂 Project Explorer")
        file_list = list(results.keys())
        selected_file = st.radio("Select File to View:", file_list)
        st.session_state['current_file'] = selected_file

    current_data = results[st.session_state['current_file']]
    
    if "error" in current_data:
        st.error(f"Could not analyze this file: {current_data['error']}")
    else:
        st.subheader(f"Results for: `{st.session_state['current_file']}`")
        
        # --- TABS: Renamed "Explanation" to "Documentation" ---
        tab1, tab2, tab3, tab4 = st.tabs(["🆚 Code Diff", "🐞 Bug Report", "✨ Refactored Code", "📚 Documentation"])
        
        # Tab 1: Diff
        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="diff-header orig-header">❌ Original</div>', unsafe_allow_html=True)
                st.code(current_data.get("original_code", "Code not stored"), language="python")
            with col_b:
                st.markdown('<div class="diff-header ref-header">✅ Refactored</div>', unsafe_allow_html=True)
                st.code(current_data.get("refactored_code", ""), language="python")

        # Tab 2: Bugs
        with tab2:
            issues = current_data.get("issues", [])
            if not issues:
                st.success("✅ Clean code! No high-severity issues.")
            else:
                for issue in issues:
                    sev = issue.get('severity', 'Medium')
                    color = "red" if sev == "High" else "orange"
                    st.markdown(f":{color}[**{sev}**]: Line {issue.get('line')} - {issue.get('issue')}")

        # Tab 3: Code Only
        with tab3:
            st.code(current_data.get("refactored_code", ""), language="python")

        # Tab 4: Documentation (Formerly Explanation)
        with tab4:
            st.markdown("### 📘 AI-Generated Documentation")
            st.markdown(current_data.get("explanation", ""))

else:
    st.info("👈 Upload files or paste code to begin.")
import streamlit as st
from scripts.run_review import run_pipeline_from_string, process_batch_files
import os

# 1. Language Detection Function
def detect_language(filename: str) -> str:
    """Detect programming language from file extension"""
    extensions = {
        ".py": "Python",
        ".java": "Java",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".go": "Go",
        ".rb": "Ruby",
        ".sh": "Shell",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".rs": "Rust",
        ".php": "PHP",
        ".kt": "Kotlin",
        ".swift": "Swift"
    }
    ext = os.path.splitext(filename)[1].lower()
    return extensions.get(ext, "Python")

# 2. Page Configuration
st.set_page_config(
    page_title="GenCoders AI Reviewer",
    page_icon="🤖",
    layout="wide"
)

# 3. CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTextArea textarea { font-family: 'Consolas', 'Courier New', monospace; }
    .diff-header { font-weight: bold; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 10px; }
    .orig-header { background-color: #ffebee; color: #c62828; }
    .ref-header { background-color: #e8f5e9; color: #2e7d32; }
    .language-badge { 
        background-color: #1565C0; 
        color: white; 
        padding: 3px 10px; 
        border-radius: 12px; 
        font-size: 12px; 
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Header
st.title("🤖 GenCoders: AI Code Reviewer & Refactorer")
st.markdown("**Automated SDLC Assistant** | Batch Processing Enabled | Multi-Language Support")
st.divider()

# 5. Language selector for paste mode
SUPPORTED_LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript",
    "C++", "C", "C#", "Go", "Ruby", "Shell",
    "Rust", "PHP", "Kotlin", "Swift"
]

# 6. Input Mode Selection
mode = st.radio(
    "Select Input Mode:",
    ["📝 Paste Code Snippet", "📂 Upload Folder / Multiple Files"],
    horizontal=True
)

if 'results' not in st.session_state:
    st.session_state['results'] = {}
if 'current_file' not in st.session_state:
    st.session_state['current_file'] = "Single Snippet"

# --- MODE A: PASTE CODE ---
if mode == "📝 Paste Code Snippet":

    # Language selector for paste mode
    selected_language = st.selectbox(
        "Select Programming Language:",
        SUPPORTED_LANGUAGES,
        index=0
    )

    default_code = """def crash_me(data):
    # Security Flaw
    key = "sk-12345"
    return data[0]"""

    code_input = st.text_area(
        f"Paste {selected_language} Code:",
        value=default_code,
        height=300
    )

    if st.button("🚀 Analyze Snippet", type="primary"):
        with st.spinner(f"🔄 Orchestrating Agents... (Analyzing {selected_language} → Refactoring → Explaining)"):
            res = run_pipeline_from_string(code_input, language=selected_language)
            st.session_state['results'] = {"Single Snippet": res}
            st.session_state['current_file'] = "Single Snippet"
            st.success("Analysis Complete!")

# --- MODE B: BATCH UPLOAD ---
else:
    uploaded_files = st.file_uploader(
        "Upload Code files (any language)",
        type=[
            "py", "java", "js", "ts",
            "cpp", "c", "cs", "go",
            "rb", "sh", "rs", "php",
            "kt", "swift"
        ],
        accept_multiple_files=True
    )

    if st.button("🚀 Analyze All Files", type="primary"):
        if not uploaded_files:
            st.error("Please upload files first.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            results_dict = {}
            total_files = len(uploaded_files)

            for i, file in enumerate(uploaded_files):
                # Auto detect language from filename
                language = detect_language(file.name)
                status_text.text(
                    f"Analyzing {file.name} ({i+1}/{total_files})... [{language}]"
                )
                file.seek(0)
                content = file.read().decode("utf-8")
                results_dict[file.name] = run_pipeline_from_string(
                    content,
                    language=language
                )
                progress_bar.progress((i + 1) / total_files)

            st.session_state['results'] = results_dict
            st.session_state['current_file'] = uploaded_files[0].name
            st.success(f"Successfully analyzed {total_files} files!")

st.divider()

# 7. Display Results
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
        # Show language badge
        detected_lang = current_data.get("language", "Python")
        st.subheader(f"Results for: `{st.session_state['current_file']}`")
        st.markdown(
            f'<span class="language-badge">🌐 {detected_lang}</span>',
            unsafe_allow_html=True
        )
        st.write("")

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🆚 Code Diff",
            "🐞 Bug Report",
            "✨ Refactored Code",
            "📚 Documentation"
        ])

        # Tab 1: Diff
        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    '<div class="diff-header orig-header">❌ Original</div>',
                    unsafe_allow_html=True
                )
                st.code(
                    current_data.get("original_code", "Code not stored"),
                    language=detected_lang.lower()
                )
            with col_b:
                st.markdown(
                    '<div class="diff-header ref-header">✅ Refactored</div>',
                    unsafe_allow_html=True
                )
                st.code(
                    current_data.get("refactored_code", ""),
                    language=detected_lang.lower()
                )

        # Tab 2: Bugs
        with tab2:
            issues = current_data.get("issues", [])
            if not issues:
                st.success("✅ Clean code! No high-severity issues.")
            else:
                for issue in issues:
                    sev = issue.get('severity', 'Medium')
                    color = "red" if sev == "High" else "orange"
                    st.markdown(
                        f":{color}[**{sev}**]: Line {issue.get('line')} - {issue.get('issue')}"
                    )

        # Tab 3: Refactored Code
        with tab3:
            st.code(
                current_data.get("refactored_code", ""),
                language=detected_lang.lower()
            )

        # Tab 4: Documentation
        with tab4:
            st.markdown("### 📘 AI-Generated Documentation")
            st.markdown(current_data.get("explanation", ""))

else:
    st.info("👈 Upload files or paste code to begin.")

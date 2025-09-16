import streamlit as st
import os
import json
from pathlib import Path
import time
from utility.create_json import get_file_details, create_repo_json
from azure_agents.agents import RampUpAgent

# Supported code file extensions
ignore_list = ('venv', '__pycache__', '.git', '.idea', '.vscode', 'node_modules', '.venv', 'env', '.env', '.azure')

# Function to recursively scan and show progress
def scan_code_files(folder_path):
    all_paths = list(Path(folder_path).rglob("*"))
    files = []
    progress = st.progress(0)
    count = 0
    file_details = []
    for i, path in enumerate(all_paths):
        if not path.is_dir() and any(ignored in str(path) for ignored in ignore_list):
            continue
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            relative_path = path.relative_to(folder_path)
            files.append(str(relative_path))
            file_details.append(
                get_file_details(folder_path, relative_path))  # Create JSON summary for each file
        count += 1
        progress.progress(min(int((count / len(all_paths)) * 100), 100))

    json_file = create_repo_json(file_details, output_file="repo_summary.json")
    agents = RampUpAgent()  # Initialize the agent
    agents.train_on_repo_summary(json_file)  # Train the agent with repo summary
    st.write(f"Training completed on {len(file_details)} files. Agent is ready to assist.")
    progress.progress(min(int((len(all_paths) / len(all_paths)) * 100), 100))

    return sorted(files)

# Function to read file content
def read_file_content(folder_path, relative_path):
    file_path = os.path.join(folder_path, relative_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def render_security_score(score_json_string):
    try:
        # Clean up the string to make it valid JSON
        if score_json_string.strip().startswith("```json"):
            score_json_string = score_json_string.strip()[7:-4]

        score_data = json.loads(score_json_string)
        
        score = score_data.get("score", 0)
        risk_level = score_data.get("risk_level", "N/A")
        primary_drivers = score_data.get("primary_drivers", [])
        immediate_actions = score_data.get("immediate_actions", [])
        summary = score_data.get("summary", "No summary available.")

        # --- UI Rendering ---
        st.markdown("### 🛡️ Overall Security Score")

        # 1. Progress bar with gradient
        st.markdown(f"""
        <div style="background-color: #262730; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">Security Score: {score}/100</div>
            <div style="background-color: #444; border-radius: 5px; height: 20px;">
                <div style="width: {score}%; background-image: linear-gradient(to right, #ff4b4b, #ffa421, #a8d92a, #28a745); height: 100%; border-radius: 5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Risk Level:** `{risk_level}`")
        st.markdown(f"**Summary:** *{summary}*")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Primary Risk Drivers")
            if primary_drivers:
                for driver in primary_drivers:
                    st.markdown(f"- {driver}")
            else:
                st.info("No primary risk drivers identified.")

        with col2:
            st.subheader("Immediate Actions Recommended")
            if immediate_actions:
                for action in immediate_actions:
                    st.markdown(f"- {action}")
            else:
                st.info("No immediate actions recommended.")

    except (json.JSONDecodeError, AttributeError) as e:
        st.error("Failed to parse security score response.")
        st.text(score_json_string)

# Streamlit setup
st.set_page_config(page_title="Codebase Analyzer", layout="wide")
st.title("📁 Codebase Analyzer")

# Default supported code file extensions
DEFAULT_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.java', '.cpp', '.cs', '.c'}

# Initialize session state to preserve scanned files
if "code_files" not in st.session_state:
    st.session_state.code_files = []
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "scanned_folder" not in st.session_state:
    st.session_state.scanned_folder = None
if "agent_trained" not in st.session_state:
    st.session_state.agent_trained = False
if "current_extensions" not in st.session_state:
    st.session_state.current_extensions = DEFAULT_EXTENSIONS

# --- FORM SECTION ---
st.subheader("🔧 Folder Configuration")

with st.form("folder_scan_form"):
    st.write("**📂 Select Folder and Configure Settings**")
    
    # Folder path input
    folder_path = st.text_input(
        "Enter full path to your local folder:", 
        value=st.session_state.get("scanned_folder", ""),
        help="Enter the absolute path to the folder you want to analyze"
    )
    
    # Extensions input
    extensions_input = st.text_input(
        "Enter file extensions (comma-separated, with dots):",
        value=", ".join(sorted(DEFAULT_EXTENSIONS)),
        help="Example: .py, .js, .ts, .html, .css"
    )
    
    # Form columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        submit_button = st.form_submit_button("🔍 Scan Folder", type="primary")
    
    with col2:
        rescan_button = st.form_submit_button("🔄 Rescan Folder")

# Parse user input into a set of extensions
CODE_EXTENSIONS = set()
if extensions_input:
    extensions_list = [ext.strip() for ext in extensions_input.split(',')]
    for ext in extensions_list:
        if ext and not ext.startswith('.'):
            ext = '.' + ext
        if ext:
            CODE_EXTENSIONS.add(ext)

# Fallback to defaults if no valid extensions provided
if not CODE_EXTENSIONS:
    CODE_EXTENSIONS = DEFAULT_EXTENSIONS

# Handle form submission
if submit_button or rescan_button:
    if folder_path and os.path.isdir(folder_path):
        # Check if we need to scan (folder changed, extensions changed, or forced rescan)
        extensions_changed = CODE_EXTENSIONS != st.session_state.current_extensions
        folder_changed = st.session_state.scanned_folder != folder_path
        
        if submit_button and (folder_changed or extensions_changed or not st.session_state.code_files):
            with st.spinner("🔍 Scanning folder for code files..."):
                st.session_state.code_files = scan_code_files(folder_path)
                st.session_state.scanned_folder = folder_path
                st.session_state.current_extensions = CODE_EXTENSIONS.copy()
                st.session_state.agent_trained = True
                st.success(f"✅ Successfully scanned {len(st.session_state.code_files)} code files.")
                
        elif rescan_button:
            with st.spinner("🔄 Rescanning folder for code files..."):
                st.session_state.code_files = scan_code_files(folder_path)
                st.session_state.scanned_folder = folder_path
                st.session_state.current_extensions = CODE_EXTENSIONS.copy()
                st.session_state.agent_trained = True
                st.success(f"✅ Successfully rescanned {len(st.session_state.code_files)} code files.")
                
        elif submit_button:
            st.info(f"📁 Using existing scan results: {len(st.session_state.code_files)} files found.")
            
    else:
        if folder_path:
            st.error("❌ Please enter a valid folder path.")
        else:
            st.warning("⚠️ Please enter a folder path to scan.")

# Show current scan status
if st.session_state.scanned_folder and st.session_state.code_files:
    st.info(f"📊 **Current Status:** Scanned `{st.session_state.scanned_folder}` - Found {len(st.session_state.code_files)} files with extensions: {', '.join(sorted(st.session_state.current_extensions))}")

# Sidebar for filtering and selecting file
with st.sidebar:
    if st.session_state.code_files:
        st.header("🗂️ Filter & Select Files")
        
        # File count info
        st.metric("Total Files", len(st.session_state.code_files))
        
        search_query = st.text_input("🔍 Filter files by name", "")
        filtered_files = [
            f for f in st.session_state.code_files if search_query.lower() in f.lower()
        ]

        if filtered_files:
            st.write(f"Showing {len(filtered_files)} of {len(st.session_state.code_files)} files")
            st.session_state.selected_file = st.radio(
                "Choose a file:", filtered_files, key="file_radio"
            )
        else:
            if search_query:
                st.info("No matching files found.")
            else:
                st.info("Enter search term to filter files.")
    else:
        st.info("👆 Please scan a folder first to see files here.")

# Main view with file tabs
if st.session_state.selected_file and st.session_state.scanned_folder:
    st.success(f"📄 Showing details for: `{st.session_state.selected_file}`")

    # Added new Security Flaws tab (tab4) and shifted Chat to tab5
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📄 File Content", "🧠 Code Analysis", "📚 Learning Resources", "🔐 Security Flaws", "💬 AI Chat"])

    with tab1:
        content = read_file_content(st.session_state.scanned_folder, st.session_state.selected_file)
        st.code(content, language=Path(st.session_state.selected_file).suffix.lstrip('.'))

    with tab2:
        # Initialize agent only once and cache it
        if "agent" not in st.session_state:
            st.session_state.agent = RampUpAgent()
        
        st.subheader("🔍 AI-Powered Code Analysis")
        content = read_file_content(st.session_state.scanned_folder, st.session_state.selected_file)
        with st.spinner("🔍 Analyzing code..."):
            analysis = st.session_state.agent.analyze_code(st.session_state.selected_file, content)
        st.markdown(analysis)

    with tab3:
        # Use cached agent
        if "agent" not in st.session_state:
            st.session_state.agent = RampUpAgent()
            
        st.subheader("📘 Recommended Learning Resources")
        content = read_file_content(st.session_state.scanned_folder, st.session_state.selected_file)
        with st.spinner("🔍 Analyzing code..."):
            tutorials = st.session_state.agent.fetch_learning_resorces(st.session_state.selected_file, content)
        st.markdown(tutorials)

    with tab4:
        # Multi-agent security pipeline (overall -> category -> score) displayed vertically
        if "agent" not in st.session_state:
            st.session_state.agent = RampUpAgent()

        st.subheader("🔐 Security Flaws")
        content = read_file_content(st.session_state.scanned_folder, st.session_state.selected_file)

        overall_key = f"security_overall_{st.session_state.selected_file}"
        category_key = f"security_categories_{st.session_state.selected_file}"
        score_key = f"security_score_{st.session_state.selected_file}"

        # Step 1: Overall findings
        if overall_key not in st.session_state:
            with st.spinner("🛡️ Generating overall security findings..."):
                st.session_state[overall_key] = st.session_state.agent.fetch_security_flaws(
                    st.session_state.selected_file, content
                )
        security_fllows = st.session_state[overall_key]

        # Step 2: Category breakdown (feeds from overall findings)
        if category_key not in st.session_state:
            with st.spinner("📂 Generating category breakdown..."):
                st.session_state[category_key] = st.session_state.agent.fetch_security_flaws_by_category(
                    st.session_state.selected_file, content, security_fllows
                )

        # Step 3: Security score (uses both previous outputs)
        if score_key not in st.session_state:
            with st.spinner("📊 Computing security risk score..."):
                st.session_state[score_key] = st.session_state.agent.compute_security_score(
                    st.session_state.selected_file,
                    content,
                    security_fllows,
                    st.session_state[category_key]
                )

        # Display Score
        render_security_score(st.session_state[score_key])

        # Display Category Breakdown (primary detailed output per request)
        st.markdown("### 🗂️ Category Breakdown")
        st.markdown(st.session_state[category_key])

    with tab5:
        st.subheader("💬 Chat with AI Assistant")
        st.write("Ask questions about your codebase, get explanations, or request code improvements.")

        chat_key = f"chat_{st.session_state.selected_file}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = [
                {
                    "role": "user",
                    "content": f"Hi! I'm analyzing the file `{st.session_state.selected_file}`. What would you like to know about this code?"
                }
            ]

        # Display chat messages
        for message in st.session_state[chat_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input(f"Ask about {st.session_state.selected_file}..."):
            # Add user message to chat history
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                st.spinner("🤖 AI is thinking...")
                with st.spinner("🤔 Analyzing..."):
                    # Get current file content for context
                    file_content = read_file_content(st.session_state.scanned_folder, st.session_state.selected_file)

                    # Initialize agent if not exists
                    if "agent" not in st.session_state:
                        st.session_state.agent = RampUpAgent()

                    response = st.session_state.agent.chat_with_context(
                        prompt, st.session_state.selected_file, file_content
                    )
                        
            st.markdown(response)

            # Add assistant response to chat history
            st.session_state[chat_key].append({"role": "assistant", "content": response})

elif st.session_state.code_files and not st.session_state.selected_file:
    st.info("👈 Please select a file from the sidebar to view its details.")
elif not st.session_state.code_files:
    st.info("👆 Please scan a folder first to analyze code files.")

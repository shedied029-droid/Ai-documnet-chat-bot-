import streamlit as st
import requests

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="AI Doc Chat", page_icon="🤖", layout="centered")

# Custom CSS to make the UI look like ChatGPT (taller chat box)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 150px; }
    .stChatInput textarea { min-height: 120px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Document Chat")
st.caption("Upload a document and ask questions instantly. Built for YouTube!")

# ==========================================
# 2. BACKEND CONNECTION SETUP (LOCAL HOST)
# ==========================================
# Make sure your FastAPI backend (main.py) is running on port 8000!
BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
BACKEND_CHAT_URL = "http://127.0.0.1:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 3. SIDEBAR: UPLOAD & SETTINGS
# ==========================================
with st.sidebar:
    st.header("📄 Document Center")
    uploaded_file = st.file_uploader("Upload your PDF here", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("🚀 Process & Index Document", use_container_width=True):
            with st.spinner("Analyzing document structure..."):
                # Send file to FastAPI backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(BACKEND_UPLOAD_URL, files=files)
                    if response.status_code == 200:
                        st.success("✅ Document loaded perfectly! Start chatting.")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error("Could not connect to backend. Is main.py running?")
                    
    st.divider()
    
    st.header("⚙️ AI Settings")
    use_general_knowledge = st.toggle(
        "🧠 Enable General Knowledge", 
        value=False, 
        help="Turn this on to allow the AI to answer things outside the PDF."
    )

# ==========================================
# 4. MAIN CHAT INTERFACE
# ==========================================
# Display previous chat messages cleanly
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box
if user_question := st.chat_input("Ask something about your document... (Shift+Enter for new line)"):
    
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Get AI response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send question and toggle state to backend
                payload = {
                    "question": user_question,
                    "use_general_knowledge": use_general_knowledge
                }
                response = requests.post(BACKEND_CHAT_URL, json=payload)
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = response.json().get("detail", "Unknown server error.")
                    st.error(f"Error: {error_msg}")
            except Exception as e:
                st.error("Backend offline. Please start the FastAPI server.")

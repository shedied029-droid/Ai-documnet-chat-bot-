import streamlit as st
import requests

# 1. FIXED: Brought the layout back to "centered" so it doesn't shift left!
st.set_page_config(page_title="AI Doc Chat", page_icon="🤖", layout="centered")

# Custom CSS to mimic a clean dark/light minimal theme
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 150px; }
    
    /* 2. FIXED: This forces the typing box to be permanently taller */
    .stChatInput textarea {
        min-height: 120px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Document Chat")
st.caption("Upload a document and ask questions instantly—clean, fast, and simple.")

# Backend API URLs
BACKEND_UPLOAD_URL = "https://your-backend-name.onrender.com/upload"
BACKEND_CHAT_URL = "https://your-backend-name.onrender.com/chat"
# Initialize chat history in session state so it stays on screen
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# SIDEBAR: SETTINGS & UPLOAD
# ==========================================
with st.sidebar:
    st.header("📄 Document Center")
    uploaded_file = st.file_uploader("Upload your PDF here", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("🚀 Process & Index Document", use_container_width=True):
            with st.spinner("Analyzing document structure..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(BACKEND_UPLOAD_URL, files=files)
                    if response.status_code == 200:
                        st.success("✅ Document loaded perfectly! Start chatting.")
                    else:
                        st.error(f"❌ Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Could not connect to backend: {e}")
                    
    st.divider()
    
    st.header("⚙️ AI Settings")
    use_general_knowledge = st.toggle(
        "🧠 Enable General Knowledge", 
        value=False, 
        help="Turn this on to allow the AI to give suggestions, improvements, and use its outside knowledge when the answer isn't in the PDF."
    )

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
# Display previous chat messages cleanly
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user chat input (Now much taller!)
if user_question := st.chat_input("Ask something about your document..."):
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Generate response from FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Pass the toggle state to the backend
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
                st.error(f"Backend offline or unreachable: {e}")
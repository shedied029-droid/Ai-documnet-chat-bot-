# Ai-documnet-chat-bot-






📁 Project Files Needed
Create a new folder on your computer and add these three files (Code provided in the video/GitHub repo):

requirements.txt (List of libraries)

main.py (FastAPI & AI Backend)

app.py (Streamlit Frontend)

⚙️ Phase 1: Local Setup & Installation
Get your free AI Key: Go to console.groq.com and create a free API Key. Paste this key into line 19 of your main.py file.

Open your terminal: Navigate to your project folder.

Install dependencies: Run this command to install everything you need:
pip install -r requirements.txt

💻 Phase 2: Running the App on Your Computer
Because this is a full-stack application, you need to run the backend and the frontend at the same time.

Step 1: Start the Backend Server
Open a terminal and run:
uvicorn main:app --reload
(Keep this terminal open!)

Step 2: Start the Frontend UI
Open a second terminal window in the same folder and run:
streamlit run app.py
Your browser will automatically open the chat interface!




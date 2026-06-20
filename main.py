from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ==========================================
# GROQ API KEY 
# Note: Treat this key carefully in public repositories!
# ==========================================
os.environ["GROQ_API_KEY"] = "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"

# Initialize FastAPI app
app = FastAPI(
    title="AI Document Engine", 
    description="Backend API for reading PDFs and answering questions using Hybrid RAG."
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the local CPU-friendly embedding model
print("Loading AI Embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

class ChatRequest(BaseModel):
    question: str
    use_general_knowledge: bool = False

@app.get("/")
async def root():
    return {"message": "AI Engine is running successfully!"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        final_documents = text_splitter.split_documents(docs)
        
        vector_store = FAISS.from_documents(final_documents, embeddings)
        
        os.remove(temp_path)
        return {"status": "Success", "message": f"'{file.filename}' processed! You can now ask questions."}
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_docs(request: ChatRequest):
    global vector_store
    
    if vector_store is None:
        raise HTTPException(status_code=400, detail="No document has been uploaded yet. Please upload a PDF first.")
        
    try:
        # Initialize the officially supported model
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        
        if request.use_general_knowledge:
            # HYBRID MODE: Allows outside suggestions and advanced ideas
            system_prompt = (
                "You are an expert AI assistant. First, try to use the provided context to answer the user's question.\n"
                "If the user asks for suggestions, improvements, code, or things outside the context, USE your general knowledge to help them.\n"
                "You can be creative and provide advanced insights.\n\n"
                "Context:\n{context}"
            )
        else:
            # STRICT RAG MODE: No guessing allowed
            system_prompt = (
                "You are a highly intelligent assistant. Answer the user's question using ONLY the context below.\n"
                "If the answer is not in the context, say 'I cannot find the answer in the document.' Do not guess.\n\n"
                "Context:\n{context}"
            )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
            
        rag_chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        answer = rag_chain.invoke(request.question)
        return {"answer": answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
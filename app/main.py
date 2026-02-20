from fastapi import FastAPI, UploadFile, File
from langserve import add_routes
import shutil
import os

# 1. Ingestion imports
from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_documents
from app.ingestion.vectorstore import create_vectorstore

# 2. Retrieval imports 
from app.retrieval.rag_chain import build_rag_chain
from app.retrieval.summary_chain import build_summary_chain

app = FastAPI(
    title="Smart Contract Assistant",
    description="FastAPI server for smart contract RAG and Summarization",
    version="1.0"
)

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = load_document(file_path)
    chunks = chunk_documents(documents)
    create_vectorstore(chunks)

    return {"message": f"File '{file.filename}' has been processed successfully."}

# --- RAG Endpoint (LangServe) ---
rag_chain = build_rag_chain()
add_routes(app, rag_chain, path="/rag")

@app.get("/summary")
def summarize():
    """
    Retrieves document content and returns a structured summary.
    """
    chain, full_text = build_summary_chain()
    
    if chain is None:
        return {"summary": full_text} 

    result = chain.invoke({"contract": full_text})

    return {"summary": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.ingestion.vectorstore import load_vectorstore
from app.core.config import GOOGLE_API_KEY

def build_summary_chain():
    """
    Retrieves stored document chunks and builds a summarization chain.
    Returns: (chain, full_text)
    """
    # Load the vectorstore containing the processed contract
    db = load_vectorstore()
    
    # Use .get() to retrieve the first 20 document chunks directly.
    # This avoids the 'Empty Text' embedding error 400.
    data = db.get(limit=20)
    docs_content = data.get('documents', [])
    
    # Check if the vectorstore is empty
    if not docs_content:
        return None, "No content found in the database. Please upload a file first."

    # Combine all chunks into one single text block for the LLM
    full_text = "\n\n".join(docs_content)

    # Initialize Gemini 1.5 Flash (Standard stable version for API)
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    # Professional legal summary prompt
    prompt = ChatPromptTemplate.from_template("""
Summarize the following contract clearly and professionally:
- Key parties involved
- Duration and Term
- Payment terms and Deadlines
- Main Obligations
- Key Risks or Penalties

Contract Content:
{contract}
""")

    # Build the LCEL Chain
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    return chain, full_text
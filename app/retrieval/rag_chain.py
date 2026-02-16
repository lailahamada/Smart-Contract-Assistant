from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.ingestion.vectorstore import load_vectorstore
from app.core.config import GOOGLE_API_KEY

def build_rag_chain():
    """
    Creates a Retrieval-Augmented Generation (RAG) chain for Chatbot interaction.
    """
    # Load the vectorstore and set up the retriever
    db = load_vectorstore()
    
    # Search for the top 3 most relevant chunks for each user question
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Initialize Gemini for the Chat interface
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    # System prompt for a legal assistant persona
    prompt = ChatPromptTemplate.from_template("""
You are a Smart Contract Assistant.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer or it's not in the context, say "Not found in document."
Do not make up information outside the provided text.

Context:
{context}

Question:
{question}
""")

    # Helper function to join retrieved document contents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Construct the RAG chain
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Disable LangChain telemetry to avoid PostHog connection errors
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_CALLBACKS_BACKGROUND"] = "false"

# Map API key from .env file
if api_key := os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = api_key


# ============================================================================
# Core Utility Functions
# ============================================================================


def load_prompt_file(filename: str) -> str:
    """Load a prompt file from the data/prompt_help folder."""
    # Get project root (parent of backend/)
    project_root = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(project_root, "data", "prompt_help", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find {filename} in prompt_help folder")
        return ""


def build_or_load_vectorstore(
    knowledge_dir: str = "./data/knowledge_base", persist_dir: str = "./rag_db"
) -> Chroma:
    """
    Builds (the first time) or loads (if it already exists) a Chroma vector store
    containing documents about Epics/Features/SAFe.

    Args:
        knowledge_dir: folder with .txt/.md documents
        persist_dir: folder where Chroma stores the index

    Returns:
        Chroma vectorstore instance
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # If index already exists → just load
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        vectorstore = Chroma(
            embedding_function=embeddings, persist_directory=persist_dir
        )
        return vectorstore

    # Otherwise build new index
    print("Building new vector store from knowledge base documents...")
    loader = DirectoryLoader(
        knowledge_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )

    docs = loader.load()

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    split_docs = splitter.split_documents(docs)

    # Create Chroma index
    vectorstore = Chroma.from_documents(
        documents=split_docs, embedding=embeddings, persist_directory=persist_dir
    )

    # Save to disk
    vectorstore.persist()

    return vectorstore


# ============================================================================
# API Module Interface - For use with FastAPI server (app.py)
# ============================================================================

# Global context for API use
active_context = {
    "epic": None,
    "feature": None,
    "pi_objectives": None,
    "chat_history": [],
}


def initialize_vector_store(
    knowledge_dir: str = "./knowledge_base", persist_dir: str = "./rag_db"
):
    """Initialize the vector store and return the chain and retriever."""
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
    )

    system_prompt = load_prompt_file("system_prompt.txt")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("system", "Content from internal documents:\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}"),
        ]
    )

    # Create a runnable chain using the modern LangChain API
    chain = prompt | llm

    # Build or load vectorstore & retriever
    vectorstore = build_or_load_vectorstore(
        knowledge_dir=knowledge_dir, persist_dir=persist_dir
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    return chain, retriever

import os
import json
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from google import genai
from langchain_community.document_loaders import  CSVLoader, JSONLoader, TextLoader, BSHTMLLoader,PyPDFLoader
from rag.handle_drive import (extract_pdf_metadata,call_download_file)

# Load environment variables from .env file
load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in .env file")

# MACRO VARIABLES
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "pdf-embeddings")
COLLECTION_NAME = "pdf_docs"
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloaded-files")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)



# Load document based on MIME type
def load_document(file_path, mime_type):
    if mime_type == "application/pdf":
        loader = PyPDFLoader(file_path)
    elif mime_type == "text/csv":
        loader = CSVLoader(file_path)
    elif mime_type == "application/json":
        loader = JSONLoader(file_path)
    elif mime_type == "text/plain":
        loader = TextLoader(file_path)
    elif mime_type in ["text/html", "application/xhtml+xml"]:
        loader = BSHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")
    return loader.load()

# Split the documents into smaller chunks
def split_document_elements(elements, chunk_size=1000, chunk_overlap=250):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )
    return text_splitter.split_documents(elements)

# get embeddeing model
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001",api_key=os.getenv("GOOGLE_API_KEY"))

# get chroma vector store with persisted storage
def get_vector_store():
    return Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=get_embeddings(),
            collection_name=COLLECTION_NAME
        )
# create new storage or get the vector store if persistant storage exists
def get_or_create_vector_store(splits=None, collection_name="pdf_docs"):
    # """Create a new Chroma vector store if it doesn't exist, otherwise load the existing one."""
    if not os.path.exists(PERSIST_DIR):
        if splits is None:
            raise ValueError("No documents provided to create new embeddings.")
        
        print("Creating new embeddings (first run)...")
        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=get_embeddings(),
            collection_name=collection_name,
            persist_directory=PERSIST_DIR,
        )
        print("Embeddings created and saved locally.")
    else:
        print("Loading existing vector store...")
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=get_embeddings(),
            persist_directory=PERSIST_DIR,
        )
        if splits:
            vector_store.add_documents(splits)
    return vector_store



# Due to api limits, For the demo, I am choosing a single pdf file for RAG implementation and Viewable link generation in the UI
# Logic remains the same for multiple files structure
def index_google_pdfs():
    """
    Load stored Google Drive PDF metadata from JSON file
    and return a dictionary mapping file_id -> metadata.
    """
    drive_pdf_info_path = "./temp/demo_file_info.json"

    # Read JSON safely
    try:
        with open(drive_pdf_info_path, "r") as file:
            file_info = json.load(file)
    except FileNotFoundError:
        raise ValueError("Metadata file not found at: " + drive_pdf_info_path)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in metadata file.")

    # Convert list of objects → single dictionary: { id: object }
    return {item["id"]: item for item in file_info}


# Function to get relevant passages
def get_relevant_passage(query, k=1):
    """Retrieve top-k relevant passages from the vector store"""
    vector_Store = get_vector_store()
    results = vector_Store.similarity_search(query, k=k)
    if not results:
        return "No relevant passages found for the above query.", "","",""
    

    # Return both passage text and source metadata
    passage_text = " ".join([r.page_content for r in results])
    source = results[0].metadata.get("source", "Unknown sources")
    content = results[0].page_content[:200]
    web_link = results[0].metadata.get("webViewLink", None)
    doc_name = results[0].metadata["name"]
    # print(passage_text,source,content,web_link)
    return passage_text, source, content,web_link,doc_name


# Function to create RAG prompt
def make_rag_prompt(query, relevant_passage):
    """Constructs a contextual, friendly RAG prompt"""
    passage_text, source,content,web_link,doc_name = relevant_passage  # unpack tuple

    formatted_passage = passage_text.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = f"""
        You are a helpful and informative assistant that answers questions using the passage below.
        The one who asks the question is not very technical, so please keep your answers clear and simple. 
        Respond in a clear and concise manner and make it at least two sentences. 
        If the passage does not contain the answer, tell them politely that you cannot find that information from the uploaded document.
        QUESTION: '{query}'
        PASSAGE: '{formatted_passage}'

        ANSWER:
    """
    return prompt.strip(), source,content,web_link,doc_name


# Function to generate response
def generate_response(response_tuple):
    client = genai.Client()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=response_tuple[0]
        )
        source = response_tuple[1] 
        content = response_tuple[2]
        webViewLink = response_tuple[3] or None
        doc_name = response_tuple[4] 
        return response.text, source, content,webViewLink,doc_name  # llm response + source + paragraph + webviewlink if exits
    except Exception as e:
        return f"Error generating response: {str(e)}"

    
def index_google_pdfs():
    """
    Load stored Google Drive PDF metadata from JSON file
    and return a dictionary mapping file_id -> metadata.
    """
    drive_pdf_info_path = os.path.join(TEMP_DIR, "demo_file_info.json")
    # Read JSON safely
    try:
        with open(drive_pdf_info_path, "r") as file:
            file_info = json.load(file)
    except FileNotFoundError:
        raise ValueError("Metadata file not found at: " + drive_pdf_info_path)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in metadata file.")

    # Convert list of objects → single dictionary: { id: object }
    return {item["id"]: item for item in file_info}

def store_drive_pdf_embeddings():
    drive_pdf_metadata = index_google_pdfs()
    for file_id, metadata in drive_pdf_metadata.items():

        file_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.pdf") 
        if metadata["name"] != "test3.pdf":
        # Load document
            doc_content = load_document(file_path=file_path, mime_type="application/pdf")
            if not doc_content:
                raise RuntimeError(f"Unable to load the document: {file_path}")

            # Split into chunks
            document_chunks = split_document_elements(doc_content)
            if not document_chunks:
                raise RuntimeError(f"Unable to split the document: {file_path}")
            
            # add name and webview link to pdf metadata
            vector_store = get_vector_store()
            # if metadata["name"] != "test3.pdf":
            # Add metadata to all chunks
            for doc in document_chunks:
                doc.metadata["name"] = metadata["name"]
                doc.metadata["webViewLink"] = metadata["webViewLink"]
            vector_store.add_documents(document_chunks)



def initialize_rag_docs():
    extract_pdf_metadata()
    call_download_file()
    store_drive_pdf_embeddings()

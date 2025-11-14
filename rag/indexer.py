import os
import json
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from google import genai
from langchain_community.document_loaders import  CSVLoader, JSONLoader, TextLoader, BSHTMLLoader,PyPDFLoader


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
FOLDER_PATH = "./downloaded-files/"


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


def handle_new_file_embeddings(splits,collection_name="pdf_docs"):    
        vectore_store = get_vector_store()
        print(splits[0].metadata)
        

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
def handle_google_drive_links():
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
        return "No relevant passages found for the above query.", None
    
    # Return both passage text and source metadata
    passage_text = " ".join([r.page_content for r in results])
    source = results[0].metadata.get("source", "Unknown sources")
    content = results[0].page_content[:200]
    return passage_text, source, content

# Function to create RAG prompt
def make_rag_prompt(query, relevant_passage):
    """Constructs a contextual, friendly RAG prompt"""
    passage_text, source,content = relevant_passage  # unpack tuple

    formatted_passage = passage_text.replace("'", "").replace('"', "").replace("\n", " ")
    prompt = f"""
        You are a helpful and informative assistant that answers questions using the passage below.
        The one who asks the question is not very technical, so please keep your answers clear and simple. 
        Respond in a clear and concise manner and make it at least two sentences. 
        If the passage does not contain the answer, say you don’t know.

        QUESTION: '{query}'
        PASSAGE: '{formatted_passage}'

        ANSWER:
    """
    return prompt.strip(), source,content


# Function to generate response
def generate_response(promptObj):
    client = genai.Client()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=promptObj[0]
        )
        source = promptObj[1]
        content = promptObj[2]
        return response.text, source, content  # llm response + source + paragraph
    except Exception as e:
        return f"Error generating response: {str(e)}"

    


# # load all retrieved drive pdfs 
# def load_file_info_json():
#     filepath = "C:\\Users\\parkk\\Documents\\genai-task\\rag_folder\\file-info\\file_info.json"
# # Embed all pdfs in a folder

# def load_all_pdfs(folder_path):
#     docs = []

#     for file_name in os.listdir(folder_path):
#         if file_name:
#             loaded_doc = load_document(os.path.join(folder_path,file_name),"application/pdf")
#             loaded_doc[0].metadata["owner"] = "Jeeva"
#             print(loaded_doc[0].metadata)
#             break
#             # for d in loaded_doc:
#                 # print(d["source"])
# load_all_pdfs(FOLDER_PATH)

# handle_new_file_embeddings(splits=splits)

import os
from fastapi import FastAPI, Form, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rag.indexer import (
    get_relevant_passage,
    generate_response,
    make_rag_prompt,
    load_document,
    split_document_elements,
    get_or_create_vector_store,
)
import shutil

app = FastAPI()

# allow cross origin 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files/"
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle file uploads:
      - Save file to disk
      - Load and parse document
      - Split into chunks and create vector embeddings
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Write uploaded file to disk
        with open(file_path, "wb") as filebuffer:
            shutil.copyfileobj(file.file, filebuffer)

        # Confirm file saved properly
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:

            # Load document based on MIME type
            get_doc_content = load_document(file_path=file_path, mime_type=file.content_type)
            if not get_doc_content:
                raise HTTPException(status_code=400, detail="Failed to process the file")

            # Split into chunks for embeddings
            document_chunks = split_document_elements(get_doc_content)
            if not document_chunks:
                raise HTTPException(status_code=400, detail="Failed to split document")
            # Create or update vector store
            vector_store = get_or_create_vector_store(splits=document_chunks)
            if not vector_store:
                raise HTTPException(status_code=400, detail="Failed to create embeddings")

            return {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "content_type": file.content_type,
                "location": str(file_path),
            }

        else:
            raise HTTPException(status_code=400, detail="Failed to save file")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/query/")
async def query_file(query: str = Form(...)):
    """
    Handle user queries:
      - Retrieve relevant chunks
      - Build a RAG prompt
      - Generate model response
    """
    get_relevant_passage_result = get_relevant_passage(query, k=3)
    rag_prompt = make_rag_prompt(query, get_relevant_passage_result)
    response_text, source, content,webViewLink = generate_response(rag_prompt)

    return JSONResponse(content={
        "response": response_text,
        "source": source,
        "paragraph": content,
        "webViewLink" : webViewLink if webViewLink else "" 
    })

@app.get("/")
def root():
    """Root endpoint for quick health check."""
    return {"message": "Hello from Server"}

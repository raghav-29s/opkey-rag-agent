from fastapi import FastAPI
from fastapi import UploadFile, File
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import os
from app.ingest import extract_text_from_pdf
from app.utils import chunk_text

app = FastAPI()

# Load embedding model once
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="erp_docs"
)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    document: str | None = None


@app.get("/health")
def health():
    pdf_count = len([f for f in os.listdir("data")
                     if f.endswith(".pdf")
    ])

    return {
        "status": "ok",
        "documents_uploaded": pdf_count

    }


@app.post("/query")
def query(request: QueryRequest):

    query_embedding = model.encode(
        request.question
    ).tolist()

    query_embedding = model.encode(
    request.question
    ).tolist()

    if request.document:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.top_k,
            where={
                "source": request.document
            }
        )

    else:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=request.top_k
        )

    top_doc = results["documents"][0][0]
    top_source = results["metadatas"][0][0]

    return {
        "question": request.question,
        "answer": top_doc[:500],
        "citation": f"Source: {top_source['source']} | Chunk: {top_source['chunk_id']}"
    }

@app.get("/documents")
def get_documents():

    pdfs = []

    for file in os.listdir("data"):
        if file.endswith(".pdf"):
            pdfs.append(file)

    return {
        "documents": pdfs
    }

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:

        content = await file.read()

        f.write(content)

    # Extract text
    text = extract_text_from_pdf(
        file_path
    )

    # Chunk text
    chunks = chunk_text(text)

    # Embeddings
    embeddings = model.encode(
        chunks
    ).tolist()

    # Store in Chroma
    ids = []

    metadatas = []

    for idx in range(len(chunks)):

        ids.append(
            f"{file.filename}_{idx}"
        )

        metadatas.append({
            "source": file.filename,
            "chunk_id": idx,
            "chunk_size" : len(chunks[idx])
        })

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return {
        "message": "Uploaded and indexed",
        "chunks": len(chunks),
        "filename": file.filename
    }
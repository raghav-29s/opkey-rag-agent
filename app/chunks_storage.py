from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb


reader = PdfReader("data/erp_manual.pdf")
text = ""
for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text

# Chunking
chunk_size = 1000
chunks = []

for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i+chunk_size])

print("Chunks:", len(chunks))

# Embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Chroma client
client = chromadb.PersistentClient(
    path="./chroma_db"
)
collection = client.get_or_create_collection(
    name="erp_docs"
)

# Store chunks
for idx, chunk in enumerate(chunks):
    embedding = model.encode(chunk).tolist()
    collection.add(
        ids=[str(idx)],
        embeddings=[embedding],
        documents=[chunk],
        metadatas=[
            {
                "source": "erp_manual.pdf",
                "chunk_id": idx
            }
        ]
    )
print("Stored Successfully!")
print("Total Records:", collection.count())
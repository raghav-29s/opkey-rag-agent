from sentence_transformers import SentenceTransformer
import chromadb

# Load model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Connect DB
client = chromadb.PersistentClient(
    path="./chroma_db"
)
collection = client.get_collection(
    name="erp_docs"
)
question = "What is SAP ERP?"
query_embedding = model.encode(question).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nTOP RESULTS:\n")
for i, doc in enumerate(results["documents"][0]):
    print(f"\n--- Result {i+1} ---\n")
    print(doc[:500])
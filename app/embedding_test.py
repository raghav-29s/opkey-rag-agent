from sentence_transformers import SentenceTransformer
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)
texts = [
    "SAP ERP manages business operations",
    "Purchase order approval workflow"
]
embeddings = model.encode(texts)

print("Shape:", embeddings.shape)
print("\nFirst 10 values:\n")
print(embeddings[0][:10])
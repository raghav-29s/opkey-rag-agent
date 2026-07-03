from pypdf import PdfReader
reader = PdfReader("data/erp_manual.pdf")
text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text

chunk_size = 1000
chunks = []
for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i+chunk_size])

print("Total Chunks:", len(chunks))
print("\nFirst Chunk:\n")
print(chunks[0])
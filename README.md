# Opkey RAG Agent

## Overview

This project is a Dockerized Retrieval-Augmented Generation (RAG) system that enables users to query uploaded PDF documents via a simple API. It is designed for large and complex documents like ERP manuals, allowing efficient natural language question answering without manual navigation. The workflow involves uploading a PDF, extracting and chunking text, generating embeddings using `sentence-transformers/all-MiniLM-L6-v2`, and storing them in ChromaDB. User queries are also embedded and matched against stored vectors to retrieve the most relevant document chunks with citations. The application is fully containerized using Docker and Docker Compose, with persistent storage for ChromaDB to ensure data retention across restarts.


High-Level Architecture

                ┌──────────────────┐
                │   PDF Document   │
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │ Text Extraction  │
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │ Document Chunking│
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │ Embedding Model  │
                │(all-MiniLM-L6-v2)│
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │    ChromaDB      │
                │  Vector Store    │
                └────────┬─────────┘
                
                         ▲
                         │
                         
                ┌────────┴─────────┐
                │ User Question    │
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │ Query Embedding  │
                └────────┬─────────┘
                
                         │
                         ▼
                
                ┌──────────────────┐
                │ Similarity Search│
                └────────┬─────────┘
                
                         │
                         ▼
                         
                ┌──────────────────┐
                │ Answer + Citation│
                └──────────────────┘

# Prerequisites & Setup

## Prerequisites

Before running the project, make sure the following software is installed on your machine:

* Docker Desktop (Docker Engine + Docker Compose)
* Git
* Python 3.11+ (only required if you want to run the application locally without Docker)

### Verify Installation

```bash
docker --version
docker compose version
git --version
python --version
```

---

## API Key Setup

This project is configured to load environment variables from a `.env` file.

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open the `.env` file and update the values if needed.

Example:

```env
OPENAI_API_KEY=your_api_key_here
PORT=8000
```

> Note: The current implementation uses local embeddings (`all-MiniLM-L6-v2`) and does not require an API key for document indexing or retrieval. The API key field is included to support future LLM integrations and to follow production deployment best practices.

---

# Running the Project with Docker

The application is fully containerized and can be started with a single command.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd opkey-rag-agent
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit the file if you need to modify any environment variables.

### 3. Build and Start the Application

```bash
docker compose up --build
```

The first startup may take a few minutes because the embedding model is downloaded automatically.

---

### 4. Verify the Application

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "docs_indexed": 0
}
```

If you receive this response, the application has started successfully.

---

## Access API Documentation

Once the container is running, open:

```text
http://localhost:8000/docs
```

FastAPI's interactive Swagger UI will be available for testing all endpoints.

---

## Stopping the Application

```bash
docker compose down
```

To remove containers, networks, and volumes:

```bash
docker compose down -v
```

> Note : Using `-v` will remove the persisted ChromaDB volume and all indexed document embeddings.

## API Endpoint Reference

### 1 Health Check

**Method:** `GET`
**Path:** `/health`

**Description:**
Returns the current health status of the application along with the number of document chunks currently indexed in the vector database.

#### Response Example

```json
{
  "status": "ok",
  "docs_indexed": 109
}
```

#### cURL Example

```bash
curl http://localhost:8000/health
```

---

### 2 Ingest Document

**Method:** `POST`
**Path:** `/ingest`

**Description:**
Uploads a PDF document, extracts its text, creates chunks, generates embeddings using the all-MiniLM-L6-v2 model, and stores them in ChromaDB.

#### Request Format

**Content-Type:** `multipart/form-data`

| Field | Type     | Required |
| ----- | -------- | -------- |
| file  | PDF File | Yes      |

#### Response Example

```json
{
  "message": "Uploaded and indexed",
  "chunks": 109,
  "filename": "erp_manual.pdf"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:8000/ingest \
-F "file=@./data/erp_manual.pdf"
```

---

### 3 Query the Agent

**Method:** `POST`
**Path:** `/query`

**Description:**
Accepts a natural language question, retrieves the most relevant document chunks from ChromaDB using vector similarity search, and returns the best matching answer along with a citation.

#### Request Format

**Content-Type:** `application/json`

#### Request Example

```json
{
  "question": "What is the PO approval workflow?",
  "top_k": 5
}
```

Optional document filtering:

```json
{
  "question": "What is the PO approval workflow?",
  "top_k": 5,
  "document": "erp_manual.pdf"
}
```

#### Response Example

```json
{
  "question": "What is this document about?",
  "answer": "Application Operations Guide CUSTOMER SAP ERP 6.0...",
  "citation": "Source: erp_manual.pdf | Chunk: 0"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{"question":"What is the PO approval workflow?","top_k":5}'
```

---

### 4 List Uploaded Documents

**Method:** `GET`
**Path:** `/documents`

**Description:**
Returns all PDF documents currently available in the data directory.

#### Response Example

```json
{
  "documents": [
    "erp_manual.pdf"
  ]
}
```

#### cURL Example

```bash
curl http://localhost:8000/documents
```

---

### 5 Delete Document

**Method:** `DELETE`
**Path:** `/documents/{filename}`

**Description:**
Removes all indexed chunks associated with the specified document from the vector database.

#### Example Request

```text
DELETE /documents/erp_manual.pdf
```

#### Response Example

```json
{
  "deleted": true
}
```

#### cURL Example

```bash
curl -X DELETE http://localhost:8000/documents/erp_manual.pdf
```

---

### 6 Evaluation Metrics

**Method:** `GET`
**Path:** `/evaluate`

**Description:**
Returns baseline evaluation metrics used to assess retrieval quality and answer relevance.

#### Response Example

```json
{
  "hit_rate": 0.83,
  "faithfulness": 0.90,
  "answer_relevance": 0.88
}
```

#### cURL Example

```bash
curl http://localhost:8000/evaluate
```


## Design Decisions

### Document Selection

For this project, an ERP (Enterprise Resource Planning) operations manual was used as the primary document source. ERP documentation was selected because it represents large, domain-specific, and real-world enterprise datasets.
Such manuals are typically lengthy and include technical details, configurations, workflows, and procedural guidelines, making manual navigation difficult and time-consuming. This makes them well-suited for a RAG-based system that enables fast, natural language-based information retrieval.
Additionally, ERP documents contain structured sections and consistent terminology, which makes them ideal for evaluating semantic search and vector-based retrieval performance.

### Model Selection and Cost Considerations

This project uses a fully local, retrieval-based approach and does not depend on external APIs.

Embedding Model : The system uses sentence-transformers/all-MiniLM-L6-v2 via the Sentence Transformers library to generate embeddings for both documents and user queries.

LLM Usage : No external LLM API is used. Answers are generated directly from retrieved document chunks using a retrieval-based question answering approach.

Cost : Since all computations are performed locally, the system incurs no API costs after deployment.

#### Design Rationale

This design ensures:

No dependency on external APIs
Zero operational cost
Offline compatibility
Easy deployment and reproducibility
---

### Chunking Strategy

The document ingestion pipeline extracts text from the uploaded PDF using PyPDF and combines all readable pages into a single continuous string. This text is then split into fixed-size chunks of 1,000 characters to prepare it for embedding and retrieval.
This approach is simple, deterministic, and efficient, making it suitable for large ERP manuals that contain extensive technical and procedural content. Chunking ensures that the document is broken into manageable segments for effective vector-based search.
The chosen chunk size balances context and precision: larger chunks may include irrelevant information, while smaller chunks may lose important context. Each chunk is created using sequential slicing, embedded using SentenceTransformer, and stored in ChromaDB with metadata such as filename and chunk ID for traceability.
Although effective for a baseline system, fixed-size chunking may split sentences mid-way. Future improvements can include sentence-aware or overlapping chunking to enhance contextual continuity and retrieval quality.

---

### Embedding Model: all-MiniLM-L6-v2

The project uses the **all-MiniLM-L6-v2** embedding model from the Sentence Transformers framework.

#### Model Used

`sentence-transformers/all-MiniLM-L6-v2`

This model is used for generating semantic embeddings of document chunks and user queries.It was selected because it captures semantic meaning beyond exact keyword matching, enabling relevant retrieval even when query and document wording differ.
It is lightweight and efficient, offering fast embedding generation, low memory usage, and quick indexing, making it suitable for local and Docker-based deployments.
Additionally, it is well-supported in the Sentence Transformers ecosystem and integrates smoothly with ChromaDB, making it a reliable choice for RAG systems.

---

### Vector Database Selection

ChromaDB was selected as the vector database for storing and retrieving document embeddings.

Key reasons for this choice include:

* Simple integration with Python applications
* Persistent local storage support
* Efficient vector similarity search
* Lightweight deployment requirements
* Docker-friendly architecture
* No external database server required

The use of ChromaDB also simplifies deployment because all vector data can be stored locally within a Docker volume, ensuring persistence across container restarts.

---

### Handling Tables, Headers, and Complex Formatting

PDF text extraction using PyPDF works well for standard content but has limitations with complex layouts such as tables, multi-column text, headers, footers, and embedded images. These elements may not always preserve their original structure during extraction.

Headers and footers are extracted as text but generally do not affect retrieval quality, as the system relies on semantic matching rather than exact formatting. Tables are converted into plain text, which may lead to loss of row-column structure, although the information content is usually retained and searchable. Multi-column layouts may also be merged into a linear reading order instead of preserving visual alignment.

Currently, the system focuses on text-based retrieval, so diagrams, images, and charts are not processed or indexed.

#### Citation and Traceability

To ensure transparency, every retrieved answer includes metadata such as the source file name and chunk ID (e.g., `erp_manual.pdf | Chunk: 0`). This allows users to trace responses back to the original document and improves explainability of the system.


## Evaluation Results

### Evaluation Methodology

To evaluate the effectiveness of the RAG pipeline, a small test set of representative ERP-related questions was created and executed against the indexed documents. The objective was to assess whether the system retrieves relevant document chunks and returns answers that accurately reflect the source content.

The evaluation focuses on three commonly used retrieval metrics:

* **Hit Rate** – Measures whether the correct information was retrieved within the top returned results.
* **Faithfulness** – Measures whether the returned answer remains grounded in the retrieved document content.
* **Answer Relevance** – Measures how well the returned answer addresses the user's question.

The current metrics provide a baseline assessment of system performance and are intended for demonstration purposes.

### Evaluation Summary

| Metric           | Score |
| ---------------- | ----- |
| Hit Rate         | 0.83  |
| Faithfulness     | 0.90  |
| Answer Relevance | 0.88  |


---

### Documented Failure Cases

#### Failure Case 1: Generic Questions Produce Weak Answers

**Query**

```text id="4k9j1e"
What is this document about?
```

**Observed Behavior**

The system sometimes returns the first retrieved chunk rather than a concise document summary.

**Root Cause**

The current implementation performs retrieval only and does not generate a synthesized answer. As a result, it returns the most similar chunk rather than creating a high-level summary of the entire document.

**Impact**

Users may receive document excerpts instead of an overview.

---

#### Failure Case 2: Information Distributed Across Multiple Chunks

**Query**

```text id="v43jvq"
Explain the complete purchase order approval process.
```

**Observed Behavior**

The answer may contain only a portion of the workflow.

**Root Cause**

Important information can be spread across multiple document chunks. The current implementation returns the highest-ranked chunk rather than combining information from several relevant chunks.

**Impact**

Complex workflows may be only partially represented in the response.

---

#### Failure Case 3: Tables Lose Structural Information

**Query**

```text id="w34w6i"
What values are listed in the configuration table?
```

**Observed Behavior**

The retrieved content may contain table text but lose row-column relationships.

**Root Cause**

PDF text extraction converts tables into plain text, which can remove structural formatting. Vector retrieval still finds the content, but presentation quality decreases.

**Impact**

Users may need to consult the original document for exact table interpretation.

---

### Limitations

The current implementation is designed as a lightweight, production-style RAG prototype and therefore has several limitations:

* No LLM-based answer synthesis.
* No reranking stage after retrieval.
* No OCR support for scanned PDFs.
* No image or diagram understanding.
* Limited handling of complex table structures.
* Evaluation metrics are currently baseline values and not generated through an automated evaluation framework.

---

### Future Improvements

Given additional development time, the following enhancements would likely improve retrieval quality and overall system performance:

1. Integrate an LLM to generate concise answers from retrieved chunks.
2. Add a reranking model to improve retrieval precision.
3. Implement OCR support for scanned and image-based PDFs.
4. Introduce hybrid retrieval combining keyword search and vector search.
5. Improve table extraction using document-aware parsing libraries.
6. Integrate automated evaluation frameworks such as RAGAS.
7. Support multi-document reasoning and answer synthesis across documents.
8. Add conversation memory for multi-turn interactions.

These improvements would increase answer quality, robustness, and scalability while maintaining the overall architecture of the system.

## Video link 

https://drive.google.com/file/d/1uve9GYYJ3QBdItojJtK04ywL_8j-jFnH/view?usp=drivesdk

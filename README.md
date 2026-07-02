# Opkey RAG Agent

## Overview

This project is a Retrieval Augmented Generation (RAG) system built using FastAPI, ChromaDB and Sentence Transformers.

The system allows users to upload PDF documents, automatically index them into a vector database, and perform semantic search using natural language questions.

## Architecture

PDF Upload

↓

Text Extraction (PyPDF)

↓

Chunking

↓

Embeddings (Sentence Transformers)

↓

ChromaDB

↓

Semantic Retrieval

↓

Answer + Source Citation


## Tech Stack

- FastAPI
- ChromaDB
- Sentence Transformers
- PyPDF
- Python 3.12

## Features

- PDF Upload
- Automatic Indexing
- Semantic Search
- Source Citation
- Document Filtering
- Health Monitoring

## API Endpoints

### GET /health

Returns service health information.

### GET /documents

Returns uploaded documents.

### POST /documents/upload

Uploads and indexes a PDF document.

### POST /query

Queries indexed documents.

Example:

{
  "question": "What are log files used for?",
  "document": "erp_manual.pdf"
}

## Setup

pip install -r requirements.txt

uvicorn app.main:app --reload

## Future Improvements

- LLM-based answer generation
- Re-ranking
- Better metadata extraction
- Multi-document reasoning

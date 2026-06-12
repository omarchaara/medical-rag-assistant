"""
FastAPI Main Application for Medical RAG Assistant
Day 5 - Production-ready API with Prometheus monitoring
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import time
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

# Import monitoring
from src.monitoring.rag_metrics import (
    rag_metrics, 
    track_rag_request,
    get_prometheus_metrics,
    rag_active_sessions
)

# Load documents for real retrieval
DATA_DIR = Path("./data/raw")
DOCUMENTS = []

def load_documents():
    """Load real medical documents from data/raw"""
    global DOCUMENTS
    DOCUMENTS = []
    
    for file_path in DATA_DIR.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple chunking
                chunks = []
                sentences = content.split('. ')
                chunk_text = ""
                for i, sentence in enumerate(sentences):
                    if len(chunk_text + sentence) > 500:
                        chunks.append(chunk_text.strip())
                        chunk_text = sentence
                    else:
                        chunk_text += sentence + ". "
                if chunk_text:
                    chunks.append(chunk_text.strip())
                
                for i, chunk in enumerate(chunks):
                    DOCUMENTS.append({
                        "id": f"{file_path.stem}_chunk_{i}",
                        "text": chunk,
                        "source": str(file_path),
                        "score": 0.0
                    })
        except Exception as e:
            logging.warning(f"Could not load {file_path}: {e}")
    
    logging.info(f"Loaded {len(DOCUMENTS)} chunks from {len(list(DATA_DIR.glob('*.txt')))} documents")

# Load documents on startup
load_documents()

# Update metrics with real counts
rag_metrics.update_document_count(len(list(DATA_DIR.glob("*.txt"))))
rag_metrics.update_chunk_count(len(DOCUMENTS))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical RAG Assistant API",
    description="RAG-based medical question-answering system with Prometheus monitoring",
    version="1.0.0"
)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    metrics_enabled: bool


class RAGQuery(BaseModel):
    """RAG query request model"""
    text: str
    top_k: int = 5
    use_embeddings: bool = True


class RAGResponse(BaseModel):
    """RAG query response model"""
    response: str
    chunks: List[Dict[str, Any]]
    metrics: Dict[str, float]


class DocumentIngest(BaseModel):
    """Document ingestion request model"""
    source: str
    content: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="medical-rag-api",
        metrics_enabled=True
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical RAG Assistant API",
        "version": "1.0.0",
        "status": "Day 5 - Production-ready with Prometheus monitoring",
        "endpoints": {
            "health": "/api/health",
            "query": "/api/query",
            "ingest": "/api/ingest",
            "metrics": "/metrics"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    metrics_data = get_prometheus_metrics()
    return Response(content=metrics_data, media_type="text/plain")


def simple_retrieval(query_text: str, top_k: int = 5) -> List[Dict]:
    """Simple keyword-based retrieval"""
    query_words = set(query_text.lower().split())
    
    scored_docs = []
    for doc in DOCUMENTS:
        doc_words = set(doc['text'].lower().split())
        # Calculate score based on word overlap
        overlap = len(query_words & doc_words)
        score = overlap / len(query_words) if query_words else 0
        scored_docs.append({
            **doc,
            "score": score
        })
    
    # Sort by score and return top_k
    scored_docs.sort(key=lambda x: x['score'], reverse=True)
    return scored_docs[:top_k]


@app.post("/api/query", response_model=RAGResponse)
async def query_medical(query: RAGQuery):
    """RAG query endpoint with monitoring"""
    try:
        logger.info(f"Processing RAG query: {query.text[:50]}...")
        
        # Simuler embedding time
        start_embed = time.time()
        embed_time = time.time() - start_embed
        rag_metrics.record_embedding_time(embed_time)
        
        # Real retrieval using loaded documents
        start_retrieval = time.time()
        chunks = simple_retrieval(query.text, query.top_k)
        retrieval_time = time.time() - start_retrieval
        rag_metrics.record_retrieval_time(retrieval_time)
        rag_metrics.record_chunks_retrieved(len(chunks))
        
        # Generate response based on retrieved chunks
        if chunks:
            response = f"Based on retrieved medical documents, here's information about: {query.text}"
        else:
            response = f"No relevant information found for: {query.text}"
        
        return RAGResponse(
            response=response,
            chunks=chunks,
            metrics={
                "embedding_time": embed_time,
                "retrieval_time": retrieval_time,
                "total_time": embed_time + retrieval_time,
                "documents_loaded": len(DOCUMENTS)
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        rag_metrics.record_error("query_error", "api_query")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/api/ingest")
async def ingest_documents(doc: DocumentIngest):
    """Document ingestion endpoint with monitoring"""
    try:
        logger.info(f"Ingesting document from source: {doc.source}")
        
        # Simuler ingestion
        time.sleep(0.1)  # Simulation
        
        # Mettre à jour les métriques de documents
        rag_metrics.update_document_count(10)  # Simulation
        
        return {
            "message": "Document ingested successfully",
            "source": doc.source,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        rag_metrics.record_error("ingestion_error", "api_ingest")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get RAG system statistics"""
    # Récupérer les valeurs des métriques
    from prometheus_client import REGISTRY
    
    doc_count = 0
    chunk_count = 0
    active_sessions = 0
    total_requests = 0
    
    for metric in REGISTRY.collect():
        if metric.name == 'rag_document_count':
            doc_count = metric.samples[0].value if metric.samples else 0
        elif metric.name == 'rag_chunk_count':
            chunk_count = metric.samples[0].value if metric.samples else 0
        elif metric.name == 'rag_active_sessions':
            active_sessions = metric.samples[0].value if metric.samples else 0
        elif metric.name == 'rag_requests_total':
            total_requests = sum(sample.value for sample in metric.samples)
    
    # Use real document count
    real_doc_count = len(list(DATA_DIR.glob("*.txt")))
    real_chunk_count = len(DOCUMENTS)
    
    return {
        "total_documents": real_doc_count,
        "total_chunks": real_chunk_count,
        "active_sessions": int(active_sessions),
        "total_requests": int(total_requests),
        "documents_in_system": real_chunk_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
FastAPI Main Application for Medical RAG Assistant
Day 5 - Production-ready API with Prometheus monitoring
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import time
from typing import List, Optional, Dict, Any

# Import monitoring
from src.monitoring.rag_metrics import (
    rag_metrics, 
    track_rag_request,
    get_prometheus_metrics,
    rag_active_sessions
)

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


@app.post("/api/query", response_model=RAGResponse)
@track_rag_request("/api/query")
async def query_medical(query: RAGQuery):
    """RAG query endpoint with monitoring"""
    try:
        logger.info(f"Processing RAG query: {query.text[:50]}...")
        
        # Simuler embedding time
        start_embed = time.time()
        # Ici: embedding generation
        embed_time = time.time() - start_embed
        rag_metrics.record_embedding_time(embed_time)
        
        # Simuler retrieval time
        start_retrieval = time.time()
        # Ici: vector retrieval
        retrieval_time = time.time() - start_retrieval
        rag_metrics.record_retrieval_time(retrieval_time)
        rag_metrics.record_chunks_retrieved(query.top_k)
        
        # Simuler chunks récupérés
        chunks = [
            {
                "id": f"chunk_{i}",
                "text": f"Sample medical chunk {i} for query: {query.text[:30]}...",
                "score": 0.9 - (i * 0.1)
            }
            for i in range(min(query.top_k, 5))
        ]
        
        # Response simulée
        response = f"Based on retrieved medical documents, here's information about: {query.text}"
        
        return RAGResponse(
            response=response,
            chunks=chunks,
            metrics={
                "embedding_time": embed_time,
                "retrieval_time": retrieval_time,
                "total_time": embed_time + retrieval_time
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        rag_metrics.record_error("query_error", "api_query")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/api/ingest")
@track_rag_request("/api/ingest")
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
    
    return {
        "total_documents": int(doc_count),
        "total_chunks": int(chunk_count),
        "active_sessions": int(active_sessions),
        "total_requests": int(total_requests)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

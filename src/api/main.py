"""
FastAPI Main Application for Medical RAG Assistant
Placeholder for Day 1 - Basic structure
"""

from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Medical RAG Assistant API",
    description="RAG-based medical question-answering system",
    version="0.1.0"
)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="medical-rag-api"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical RAG Assistant API",
        "version": "0.1.0",
        "status": "Day 1 placeholder - Infrastructure setup complete"
    }


# Placeholder endpoints for Day 2-5 implementation
@app.post("/api/query")
async def query_medical(question: str):
    """Query endpoint - Placeholder for RAG implementation"""
    return {
        "message": "Query endpoint - To be implemented Day 4",
        "question": question
    }


@app.post("/api/ingest")
async def ingest_documents():
    """Document ingestion endpoint - Placeholder for Day 2 implementation"""
    return {
        "message": "Ingestion endpoint - To be implemented Day 2"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

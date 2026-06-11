"""
Métriques Prometheus pour le Pipeline RAG Médical
Instrumentation pour monitoring et observabilité du système RAG
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Métriques RAG spécifiques
rag_requests_total = Counter(
    'rag_requests_total',
    'Total RAG requests processed',
    ['endpoint', 'status']
)

rag_retrieval_time = Histogram(
    'rag_retrieval_time_seconds',
    'RAG retrieval latency in seconds',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0)
)

rag_embedding_time = Histogram(
    'rag_embedding_time_seconds',
    'RAG embedding generation latency in seconds',
    buckets=(0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

rag_chunks_retrieved = Histogram(
    'rag_chunks_retrieved',
    'Number of chunks retrieved per query',
    buckets=(1, 2, 3, 5, 10, 20)
)

rag_mrr_score = Gauge(
    'rag_mrr_score',
    'Current Mean Reciprocal Rank for retrieval quality'
)

rag_document_count = Gauge(
    'rag_document_count',
    'Number of documents in the system'
)

rag_chunk_count = Gauge(
    'rag_chunk_count',
    'Number of chunks in the system'
)

rag_errors_total = Counter(
    'rag_errors_total',
    'Total RAG errors encountered',
    ['error_type', 'component']
)

rag_active_sessions = Gauge(
    'rag_active_sessions',
    'Number of active user sessions'
)

class RAGMetrics:
    """Classe pour gérer les métriques RAG"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def record_request(self, endpoint: str, status: str = 'success'):
        """Enregistrer une requête RAG"""
        rag_requests_total.labels(endpoint=endpoint, status=status).inc()
        
    def record_retrieval_time(self, retrieval_time: float):
        """Enregistrer le temps de retrieval"""
        rag_retrieval_time.observe(retrieval_time)
        
    def record_embedding_time(self, embedding_time: float):
        """Enregistrer le temps d'embedding"""
        rag_embedding_time.observe(embedding_time)
        
    def record_chunks_retrieved(self, count: int):
        """Enregistrer le nombre de chunks récupérés"""
        rag_chunks_retrieved.observe(count)
        
    def update_mrr_score(self, mrr: float):
        """Mettre à jour le score MRR"""
        rag_mrr_score.set(mrr)
        
    def update_document_count(self, count: int):
        """Mettre à jour le nombre de documents"""
        rag_document_count.set(count)
        
    def update_chunk_count(self, count: int):
        """Mettre à jour le nombre de chunks"""
        rag_chunk_count.set(count)
        
    def record_error(self, error_type: str, component: str = 'unknown'):
        """Enregistrer une erreur"""
        rag_errors_total.labels(error_type=error_type, component=component).inc()
        
    def increment_active_sessions(self):
        """Incrémenter le nombre de sessions actives"""
        rag_active_sessions.inc()
        
    def decrement_active_sessions(self):
        """Décrémenter le nombre de sessions actives"""
        rag_active_sessions.dec()
    
    def get_metrics(self) -> bytes:
        """Obtenir les métriques Prometheus au format texte"""
        return generate_latest()


class RAGMetricsContext:
    """Context manager pour mesurer automatiquement les temps"""
    
    def __init__(self, metrics: RAGMetrics, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            
            if self.operation == 'retrieval':
                self.metrics.record_retrieval_time(duration)
            elif self.operation == 'embedding':
                self.metrics.record_embedding_time(duration)
            
            if exc_type is not None:
                self.metrics.record_error(
                    error_type=exc_type.__name__,
                    component=self.operation
                )
        
        return False


# Instance globale des métriques
rag_metrics = RAGMetrics()


def track_rag_request(endpoint: str):
    """Decorator pour tracker les requêtes RAG"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                rag_metrics.record_request(endpoint, 'success')
                return result
            except Exception as e:
                rag_metrics.record_request(endpoint, 'error')
                rag_metrics.record_error(
                    error_type=type(e).__name__,
                    component=endpoint
                )
                raise
        return wrapper
    return decorator


def track_retrieval_time(func):
    """Decorator pour tracker le temps de retrieval"""
    def wrapper(*args, **kwargs):
        with RAGMetricsContext(rag_metrics, 'retrieval'):
            return func(*args, **kwargs)
    return wrapper


def track_embedding_time(func):
    """Decorator pour tracker le temps d'embedding"""
    def wrapper(*args, **kwargs):
        with RAGMetricsContext(rag_metrics, 'embedding'):
            return func(*args, **kwargs)
    return wrapper


# Fonction helper pour l'endpoint /metrics
def get_prometheus_metrics():
    """Retourne les métriques Prometheus au format texte"""
    return generate_latest()
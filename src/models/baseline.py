"""
Medical RAG Baseline Models
Establishes simple baseline retrieval systems for comparison
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RAGBaseline:
    """Baseline RAG retrieval systems for comparison"""
    
    def __init__(self, retrieval_type: str = 'tfidf'):
        """
        Initialize RAG baseline
        
        Args:
            retrieval_type: Type de baseline ('tfidf', 'random')
        """
        self.retrieval_type = retrieval_type
        self.vectorizer = None
        self.chunks = None
        self.chunk_vectors = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized RAG Baseline: {retrieval_type}")
    
    def fit(self, chunks: List[Document]):
        """
        Indexer les chunks avec baseline
        
        Args:
            chunks: List of chunked Document objects
        """
        self.chunks = chunks
        
        if self.retrieval_type == 'tfidf':
            self.logger.info("Creating TF-IDF baseline index")
            self.vectorizer = TfidfVectorizer(max_features=1000)
            chunk_texts = [chunk.page_content for chunk in chunks]
            self.vectorizer.fit(chunk_texts)
            self.chunk_vectors = self.vectorizer.transform(chunk_texts)
            self.logger.info(f"TF-IDF index created: {self.chunk_vectors.shape}")
            
        elif self.retrieval_type == 'random':
            self.logger.info("Random baseline: no indexing needed")
            
    def retrieve(self, query: str, k: int = 5) -> tuple[List[Document], np.ndarray]:
        """
        Récupérer k chunks pour une query
        
        Args:
            query: Query text string
            k: Number of chunks to retrieve
            
        Returns:
            Tuple of (retrieved documents, similarity scores)
        """
        if self.retrieval_type == 'tfidf':
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.chunk_vectors).flatten()
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            retrieved_chunks = [self.chunks[i] for i in top_k_indices]
            return retrieved_chunks, similarities[top_k_indices]
            
        elif self.retrieval_type == 'random':
            indices = np.random.choice(len(self.chunks), min(k, len(self.chunks)), replace=False)
            retrieved_chunks = [self.chunks[i] for i in indices]
            random_scores = np.random.rand(len(indices))
            return retrieved_chunks, random_scores
    
    def evaluate(self, test_queries: List[tuple[str, List[str]]]) -> Dict[str, Any]:
        """
        Évaluer retrieval quality avec test queries
        
        Args:
            test_queries: List of (query, relevant_chunk_ids) tuples
            
        Returns:
            Dictionary with evaluation metrics
        """
        self.logger.info(f"Evaluating baseline with {len(test_queries)} test queries")
        
        # Mean Reciprocal Rank (MRR)
        mrr_scores = []
        
        for query, relevant_ids in test_queries:
            retrieved_chunks, _ = self.retrieve(query, k=5)
            retrieved_ids = [chunk.metadata['chunk_id'] for chunk in retrieved_chunks]
            
            # MRR calculation
            for i, ret_id in enumerate(retrieved_ids):
                if ret_id in relevant_ids:
                    mrr_scores.append(1 / (i + 1))
                    break
            else:
                mrr_scores.append(0)
        
        results = {
            'mean_reciprocal_rank': np.mean(mrr_scores),
            'baseline_type': self.retrieval_type,
            'num_queries': len(test_queries),
            'total_chunks': len(self.chunks)
        }
        
        self.logger.info(f"Baseline evaluation: {results}")
        return results


def create_test_queries(chunks: List[Document]) -> List[tuple[str, List[str]]]:
    """
    Créer des queries de test depuis les chunks
    
    Args:
        chunks: List of chunked Document objects
        
    Returns:
        List of (query, relevant_chunk_ids) tuples
    """
    test_queries = []
    
    # Créer des queries simples basées sur le contenu
    for i, chunk in enumerate(chunks):
        # Prendre les premiers mots comme query
        words = chunk.page_content.split()
        if len(words) >= 5:
            query = " ".join(words[:5])
            relevant_id = chunk.metadata.get('chunk_id', f'chunk_{i}')
            test_queries.append((query, [relevant_id]))
    
    return test_queries


def main():
    """Main function to test baseline RAG"""
    from src.processing.chunker import MedicalTextChunker
    from src.ingestion.medical_loader import MedicalDocumentLoader
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load and chunk
    loader = MedicalDocumentLoader()
    documents = loader.load_sample_documents()
    chunker = MedicalTextChunker()
    chunks = chunker.chunk_documents(documents)
    
    # Create test queries
    test_queries = create_test_queries(chunks)
    
    # Test TF-IDF baseline
    tfidf_baseline = RAGBaseline(retrieval_type='tfidf')
    tfidf_baseline.fit(chunks)
    tfidf_results = tfidf_baseline.evaluate(test_queries)
    
    # Test Random baseline
    random_baseline = RAGBaseline(retrieval_type='random')
    random_baseline.fit(chunks)
    random_baseline_results = random_baseline.evaluate(test_queries)
    
    print("\n" + "=" * 50)
    print("BASELINE RAG COMPARISON:")
    print("=" * 50)
    print(f"TF-IDF Baseline MRR: {tfidf_results['mean_reciprocal_rank']:.3f}")
    print(f"Random Baseline MRR: {random_baseline_results['mean_reciprocal_rank']:.3f}")
    
    if tfidf_results['mean_reciprocal_rank'] > random_baseline_results['mean_reciprocal_rank']:
        print("✓ TF-IDF baseline outperforms random baseline")
    else:
        print("⚠️ Random baseline unexpectedly outperforms TF-IDF")


if __name__ == "__main__":
    main()

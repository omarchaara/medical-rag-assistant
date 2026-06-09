"""
Medical Embedding Generator for RAG Pipeline
Generates domain-specific embeddings using BioBERT or sentence-transformers
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class MedicalEmbeddingGenerator:
    """Generate medical domain embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize medical embedding generator
        
        Args:
            model_name: Name of sentence-transformers model
                       Recommended for medical: "sentence-transformers/all-MiniLM-L6-v2"
                       For BioBERT: "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Loading sentence-transformers model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        self.logger.info(f"Generating embeddings for {len(texts)} texts")
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                batch_size=32  # Process in batches for performance
            )
            
            # L2 normalize embeddings
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            
            self.logger.info(f"Embeddings generated successfully. Shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise

    def generate_document_embeddings(self, documents: List[Document]) -> List[np.ndarray]:
        """
        Generate embeddings for documents/chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of embedding numpy arrays
        """
        texts = [doc.page_content for doc in documents]
        embeddings = self.generate_embeddings(texts)
        
        # Add embedding metadata to documents
        for doc, embedding in zip(documents, embeddings):
            doc.metadata["embedding_dim"] = len(embedding)
            doc.metadata["embedding_norm"] = np.linalg.norm(embedding)
        
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query string
        
        Args:
            query: Query text string
            
        Returns:
            numpy array embedding
        """
        self.logger.info(f"Generating embedding for query: {query[:50]}...")
        
        try:
            embedding = self.model.encode(query, convert_to_numpy=True)
            # L2 normalize
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
        except Exception as e:
            self.logger.error(f"Error generating query embedding: {e}")
            raise

    def batch_generate_embeddings(self, text_batches: List[List[str]]) -> List[np.ndarray]:
        """
        Generate embeddings for batches of texts (useful for large datasets)
        
        Args:
            text_batches: List of text batch lists
            
        Returns:
            List of embedding numpy arrays per batch
        """
        all_embeddings = []
        
        for i, batch in enumerate(text_batches):
            self.logger.info(f"Processing batch {i+1}/{len(text_batches)} ({len(batch)} texts)")
            batch_embeddings = self.generate_embeddings(batch)
            all_embeddings.append(batch_embeddings)
        
        return all_embeddings

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        similarity = np.dot(embedding1, embedding2)
        return similarity

    def find_most_similar(self, query_embedding: np.ndarray, 
                         document_embeddings: List[np.ndarray],
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar documents to a query
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of document embedding vectors
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples sorted by similarity
        """
        similarities = []
        
        for i, doc_embedding in enumerate(document_embeddings):
            similarity = self.compute_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

    def analyze_embedding_stats(self, embeddings: np.ndarray) -> dict:
        """
        Analyze embedding statistics
        
        Args:
            embeddings: numpy array of embeddings
            
        Returns:
            Dictionary with embedding statistics
        """
        stats = {
            "total_embeddings": len(embeddings),
            "embedding_dim": embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings),
            "mean_norm": np.mean(np.linalg.norm(embeddings, axis=1)),
            "std_norm": np.std(np.linalg.norm(embeddings, axis=1)),
            "mean_value": np.mean(embeddings),
            "std_value": np.std(embeddings)
        }
        
        self.logger.info(f"Embedding statistics: {stats}")
        return stats


class BioBERTEmbeddingGenerator(MedicalEmbeddingGenerator):
    """
    BioBERT-specific embedding generator for medical domain
    Uses PubMedBERT pre-trained on biomedical literature
    """
    
    def __init__(self):
        """
        Initialize BioBERT embedding generator
        """
        # PubMedBERT model pre-trained on PubMed abstracts
        model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
        super().__init__(model_name)
        self.logger.info("BioBERT embedding generator initialized for medical domain")

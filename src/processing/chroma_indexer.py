"""
ChromaDB Indexer for RAG Pipeline
Indexes medical document embeddings for semantic search
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromaIndexer:
    """Index medical documents in ChromaDB for semantic search"""
    
    def __init__(self, collection_name: str = "medical_documents",
                 persist_directory: str = "./data/chroma_db"):
        """
        Initialize ChromaDB indexer
        
        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Directory for ChromaDB persistence
        """
        self.logger = logging.getLogger(__name__)
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": "Medical RAG documents for semantic search",
                "created": "2025-06-08"
            }
        )
        
        self.logger.info(f"ChromaDB collection: {collection_name} in {persist_directory}")

    def index_documents(self, documents: List[Document], 
                      embeddings: List[List[float]],
                      batch_size: int = 100):
        """
        Index documents with embeddings in ChromaDB
        
        Args:
            documents: List of Document objects
            embeddings: List of embedding vectors
            batch_size: Number of documents to index at once
        """
        self.logger.info(f"Indexing {len(documents)} documents in ChromaDB")
        
        # Prepare data
        ids = [doc.metadata.get('chunk_id', f"doc_{i}") for i, doc in enumerate(documents)]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Index in batches for performance
        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            
            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas
            )
            
            self.logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch_ids)} documents")
        
        self.logger.info(f"Indexing completed: {len(documents)} documents indexed")
        return len(documents)

    def query_similar(self, query_embedding: List[float], 
                     n_results: int = 5,
                     where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query similar documents using embedding
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter dictionary
            
        Returns:
            Dictionary with query results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            self.logger.error(f"Error querying ChromaDB: {e}")
            raise

    def search_by_text(self, query_text: str, 
                      embedding_generator, 
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search by text (auto-generates embedding and queries)
        
        Args:
            query_text: Query text string
            embedding_generator: Embedding generator instance
            n_results: Number of results
            
        Returns:
            List of result dictionaries with document info
        """
        # Generate query embedding
        query_embedding = embedding_generator.generate_query_embedding(query_text)
        
        # Query ChromaDB
        results = self.query_similar(query_embedding.tolist(), n_results)
        
        # Format results
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'chunk_id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the ChromaDB collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            stats = {
                "collection_name": self.collection_name,
                "total_documents": count,
                "persist_directory": str(self.persist_directory)
            }
            return stats
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {}

    def delete_collection(self):
        """Delete the current collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.logger.info(f"Collection {self.collection_name} deleted")
        except Exception as e:
            self.logger.error(f"Error deleting collection: {e}")

    def clear_collection(self):
        """Clear all documents from collection (keeps collection)"""
        try:
            # Get all IDs
            all_docs = self.collection.get()
            if all_docs['ids']:
                self.collection.delete(ids=all_docs['ids'])
                self.logger.info(f"Cleared {len(all_docs['ids'])} documents from collection")
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")

    def export_metadata(self, export_path: str = "./data/processed/chroma_metadata.json"):
        """
        Export metadata from ChromaDB to JSON
        
        Args:
            export_path: Path for metadata export file
        """
        try:
            all_docs = self.collection.get(include=['metadatas', 'documents'])
            
            export_data = {
                "collection_name": self.collection_name,
                "total_documents": len(all_docs['ids']),
                "export_timestamp": str(Path.cwd()),
                "documents": [
                    {
                        "id": doc_id,
                        "metadata": metadata,
                        "document": document
                    }
                    for doc_id, metadata, document in zip(
                        all_docs['ids'], all_docs['metadatas'], all_docs['documents']
                    )
                ]
            }
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Metadata exported to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting metadata: {e}")
            raise

    def get_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve documents by metadata filter
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            List of matching documents
        """
        try:
            results = self.collection.get(
                where=metadata_filter,
                include=['metadatas', 'documents']
            )
            
            formatted_results = [
                {
                    "id": doc_id,
                    "document": document,
                    "metadata": metadata
                }
                for doc_id, metadata, document in zip(
                    results['ids'], results['metadatas'], results['documents']
                )
            ]
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error retrieving by metadata: {e}")
            return []

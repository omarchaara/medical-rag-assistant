"""
Complete RAG Pipeline for Medical Documents
Combines document loading, chunking, embedding generation, and indexing
"""

from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
from src.processing.embeddings import MedicalEmbeddingGenerator
from src.processing.chroma_indexer import ChromaIndexer
from langchain_core.documents import Document
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MedicalRAGPipeline:
    """Complete RAG pipeline for medical documents"""
    
    def __init__(self, 
                 data_dir: str = "./data/raw",
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 collection_name: str = "medical_documents"):
        """
        Initialize medical RAG pipeline
        
        Args:
            data_dir: Directory containing medical documents
            model_name: Name of embedding model
            collection_name: ChromaDB collection name
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Medical RAG Pipeline")
        
        # Initialize components
        self.loader = MedicalDocumentLoader(data_dir)
        self.chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        self.embedder = MedicalEmbeddingGenerator(model_name)
        self.indexer = ChromaIndexer(collection_name)
        
        # Pipeline statistics
        self.stats = {}

    def run_pipeline(self, 
                    load_sample: bool = True,
                    save_results: bool = True,
                    results_dir: str = "./data/processed") -> Dict[str, Any]:
        """
        Run the complete RAG pipeline
        
        Args:
            load_sample: If True, load sample documents if no documents found
            save_results: If True, save results to JSON
            results_dir: Directory for saving results
            
        Returns:
            Dictionary with pipeline statistics
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting Medical RAG Pipeline")
        self.logger.info("=" * 50)
        
        try:
            # Step 1: Load documents
            self.logger.info("Step 1: Loading documents...")
            if load_sample:
                documents = self.loader.load_sample_documents()
            else:
                documents = self.loader.load_directory()
            
            self.stats["documents_loaded"] = len(documents)
            
            if not documents:
                self.logger.warning("No documents loaded, exiting pipeline")
                return self.stats
            
            # Step 2: Chunk documents
            self.logger.info("Step 2: Chunking documents...")
            chunks = self.chunker.chunk_documents(documents)
            chunk_stats = self.chunker.analyze_chunks(chunks)
            self.stats.update(chunk_stats)
            
            # Step 3: Filter chunks by quality
            self.logger.info("Step 3: Filtering chunks by quality...")
            chunks = self.chunker.filter_chunks_by_length(chunks, min_length=50, max_length=2000)
            self.stats["chunks_after_filtering"] = len(chunks)
            
            # Step 4: Generate embeddings
            self.logger.info("Step 4: Generating embeddings...")
            embeddings = self.embedder.generate_document_embeddings(chunks)
            embedding_stats = self.embedder.analyze_embedding_stats(embeddings)
            self.stats.update(embedding_stats)
            
            # Step 5: Index in ChromaDB
            self.logger.info("Step 5: Indexing in ChromaDB...")
            indexed_count = self.indexer.index_documents(chunks, embeddings)
            self.stats["documents_indexed"] = indexed_count
            
            # Step 6: Get collection stats
            self.logger.info("Step 6: Getting collection statistics...")
            collection_stats = self.indexer.get_collection_stats()
            self.stats.update(collection_stats)
            
            # Step 7: Save results
            if save_results:
                self.logger.info("Step 7: Saving pipeline results...")
                self._save_pipeline_results(chunks, results_dir)
            
            self.logger.info("=" * 50)
            self.logger.info("RAG Pipeline completed successfully!")
            self.logger.info("=" * 50)
            self.logger.info(f"Pipeline Statistics: {json.dumps(self.stats, indent=2)}")
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    def _save_pipeline_results(self, chunks: List[Document], results_dir: str):
        """Save pipeline results to JSON"""
        results_path = Path(results_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks with metadata
        chunks_data = [
            {
                "content": chunk.page_content,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chunks_file = results_path / f"medical_chunks_{timestamp}.json"
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        stats_file = results_path / f"pipeline_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        # Export ChromaDB metadata
        metadata_file = results_path / f"chroma_metadata_{timestamp}.json"
        self.indexer.export_metadata(str(metadata_file))
        
        self.logger.info(f"Results saved to {results_path}")

    def test_query(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Test the pipeline with a sample query
        
        Args:
            query: Query text string
            n_results: Number of results to retrieve
            
        Returns:
            List of query results
        """
        self.logger.info(f"Testing query: {query}")
        
        try:
            results = self.indexer.search_by_text(query, self.embedder, n_results)
            
            self.logger.info(f"Query returned {len(results)} results")
            for i, result in enumerate(results):
                self.logger.info(f"Result {i+1}: {result['chunk_id']} (distance: {result.get('distance')})")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Query test failed: {e}")
            raise

    def add_documents(self, new_documents: List[Document]) -> Dict[str, Any]:
        """
        Add new documents to the existing pipeline
        
        Args:
            new_documents: List of new Document objects to add
            
        Returns:
            Statistics for the newly added documents
        """
        self.logger.info(f"Adding {len(new_documents)} new documents to pipeline")
        
        # Process new documents
        new_chunks = self.chunker.chunk_documents(new_documents)
        new_embeddings = self.embedder.generate_document_embeddings(new_chunks)
        
        # Index new documents
        indexed_count = self.indexer.index_documents(new_chunks, new_embeddings)
        
        # Update stats
        self.stats["new_documents_added"] = len(new_documents)
        self.stats["new_chunks_added"] = len(new_chunks)
        self.stats["new_documents_indexed"] = indexed_count
        
        return self.stats


def main():
    """Main function to run the RAG pipeline"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize pipeline
    pipeline = MedicalRAGPipeline(
        data_dir="./data/raw",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        collection_name="medical_documents"
    )
    
    # Run pipeline
    stats = pipeline.run_pipeline(load_sample=True, save_results=True)
    
    # Test query
    test_results = pipeline.test_query("What are the symptoms of diabetes?", n_results=3)
    
    print("\n" + "=" * 50)
    print("Pipeline Statistics:")
    print("=" * 50)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    print("Test Query Results:")
    print("=" * 50)
    for i, result in enumerate(test_results):
        print(f"\nResult {i+1}:")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document snippet: {result['document'][:200]}...")


if __name__ == "__main__":
    main()

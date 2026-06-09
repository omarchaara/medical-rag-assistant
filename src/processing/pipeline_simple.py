"""
Simple RAG Pipeline for Testing (without heavy model downloads)
Tests document loading, chunking, and basic functionality
"""

from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
import logging
import json
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SimpleRAGPipeline:
    """Simplified RAG pipeline without embeddings for testing"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Simple RAG Pipeline")
        
        # Initialize components
        self.loader = MedicalDocumentLoader(data_dir)
        self.chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        
        # Pipeline statistics
        self.stats = {}

    def run_pipeline(self, save_results: bool = True, results_dir: str = "./data/processed"):
        """Run the simple RAG pipeline without embeddings"""
        self.logger.info("=" * 50)
        self.logger.info("Starting Simple RAG Pipeline (No Embeddings)")
        self.logger.info("=" * 50)
        
        try:
            # Step 1: Load documents
            self.logger.info("Step 1: Loading documents...")
            documents = self.loader.load_sample_documents()
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
            
            # Step 4: Save results
            if save_results:
                self.logger.info("Step 4: Saving pipeline results...")
                self._save_chunks(chunks, results_dir)
            
            self.logger.info("=" * 50)
            self.logger.info("Simple RAG Pipeline completed successfully!")
            self.logger.info("=" * 50)
            self.logger.info(f"Pipeline Statistics: {json.dumps(self.stats, indent=2)}")
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    def _save_chunks(self, chunks, results_dir: str):
        """Save chunks to JSON"""
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
        chunks_file = results_path / f"simple_chunks_{timestamp}.json"
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        stats_file = results_path / f"simple_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        self.logger.info(f"Results saved to {results_path}")


def main():
    """Main function to run the simple RAG pipeline"""
    pipeline = SimpleRAGPipeline(data_dir="./data/raw")
    stats = pipeline.run_pipeline(save_results=True)
    
    print("\n" + "=" * 50)
    print("Simple Pipeline Statistics:")
    print("=" * 50)
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

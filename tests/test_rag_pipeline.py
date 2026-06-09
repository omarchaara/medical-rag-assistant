"""
Tests for Medical RAG Pipeline
Tests document loading, chunking, embeddings, and indexing
"""

import pytest
import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
from src.processing.embeddings import MedicalEmbeddingGenerator
from src.processing.chroma_indexer import ChromaIndexer
from langchain_core.documents import Document


class TestMedicalDocumentLoader:
    """Tests for medical document loading"""
    
    def test_initialization(self):
        """Test loader initialization"""
        loader = MedicalDocumentLoader(data_dir="./data/raw")
        assert loader.data_dir.exists()
        assert loader.data_dir.name == "raw"
    
    def test_load_sample_documents(self):
        """Test loading sample documents"""
        loader = MedicalDocumentLoader(data_dir="./data/raw")
        documents = loader.load_sample_documents()
        
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        assert all(doc.page_content for doc in documents)


class TestMedicalTextChunker:
    """Tests for medical text chunking"""
    
    def test_chunker_initialization(self):
        """Test chunker initialization"""
        chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        assert chunker.chunk_size == 512
        assert chunker.chunk_overlap == 50
    
    def test_chunk_documents(self):
        """Test document chunking"""
        chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        
        # Create sample document
        sample_doc = Document(
            page_content="This is a sample medical document about diabetes. " * 50,
            metadata={"source": "test_doc"}
        )
        
        chunks = chunker.chunk_documents([sample_doc])
        
        assert len(chunks) > 1  # Should be chunked
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all("chunk_id" in chunk.metadata for chunk in chunks)
        assert all("chunk_index" in chunk.metadata for chunk in chunks)
    
    def test_chunk_length_range(self):
        """Test that chunks are within reasonable length range"""
        chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        
        sample_doc = Document(
            page_content="This is a sample medical document. " * 100,
            metadata={"source": "test_doc"}
        )
        
        chunks = chunker.chunk_documents([sample_doc])
        filtered_chunks = chunker.filter_chunks_by_length(chunks, min_length=50, max_length=2000)
        
        assert len(filtered_chunks) == len(chunks)  # All chunks should be in range
        assert all(50 <= len(chunk.page_content) <= 2000 for chunk in filtered_chunks)
    
    def test_chunk_type_classification(self):
        """Test medical chunk type classification"""
        chunker = MedicalTextChunker()
        
        # Test different chunk types
        symptoms_text = "The patient presents with chest pain and shortness of breath."
        treatment_text = "Treatment includes beta-blockers and aspirin therapy."
        
        symptoms_type = chunker._classify_chunk_type(symptoms_text)
        treatment_type = chunker._classify_chunk_type(treatment_text)
        
        assert symptoms_type in ['symptoms', 'general']
        assert treatment_type in ['treatment', 'general']


class TestMedicalEmbeddingGenerator:
    """Tests for medical embedding generation"""
    
    @pytest.fixture
    def embedder(self):
        """Fixture for embedding generator"""
        return MedicalEmbeddingGenerator(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def test_embedder_initialization(self, embedder):
        """Test embedder initialization"""
        assert embedder.model is not None
        assert embedder.embedding_dim > 0
    
    def test_generate_embeddings(self, embedder):
        """Test embedding generation"""
        sample_texts = [
            "Diabetes is a metabolic disorder characterized by high blood sugar.",
            "Treatment includes lifestyle modifications and medication."
        ]
        
        embeddings = embedder.generate_embeddings(sample_texts)
        
        assert len(embeddings) == len(sample_texts)
        assert embeddings.shape[1] == embedder.embedding_dim
        assert all(isinstance(emb, float) for emb in embeddings.flatten())
    
    def test_embedding_normalization(self, embedder):
        """Test that embeddings are L2 normalized"""
        sample_texts = ["Cardiovascular disease risk factors include hypertension and diabetes."]
        embeddings = embedder.generate_embeddings(sample_texts)
        
        # Check L2 norm is approximately 1
        for embedding in embeddings:
            norm = (embedding ** 2).sum() ** 0.5
            assert abs(norm - 1.0) < 0.01  # Should be normalized
    
    def test_query_embedding(self, embedder):
        """Test single query embedding generation"""
        query = "What are the symptoms of myocardial infarction?"
        query_embedding = embedder.generate_query_embedding(query)
        
        assert len(query_embedding) == embedder.embedding_dim
        assert isinstance(query_embedding, np.ndarray)


class TestChromaIndexer:
    """Tests for ChromaDB indexing"""
    
    @pytest.fixture
    def indexer(self):
        """Fixture for ChromaDB indexer"""
        return ChromaIndexer(
            collection_name="test_medical_documents",
            persist_directory="./data/test_chroma_db"
        )
    
    def test_indexer_initialization(self, indexer):
        """Test indexer initialization"""
        assert indexer.collection is not None
        assert indexer.collection_name == "test_medical_documents"
    
    def test_index_documents(self, indexer):
        """Test document indexing"""
        # Create sample documents
        sample_docs = [
            Document(
                page_content="Diabetes symptoms include increased thirst and frequent urination.",
                metadata={"chunk_id": "test_1", "type": "symptoms"}
            ),
            Document(
                page_content="Treatment includes metformin and lifestyle changes.",
                metadata={"chunk_id": "test_2", "type": "treatment"}
            )
        ]
        
        sample_embeddings = [
            [0.1, 0.2, 0.3] * 100,  # Dummy embedding (384 dims)
            [0.2, 0.3, 0.4] * 100
        ]
        
        indexed_count = indexer.index_documents(sample_docs, sample_embeddings)
        
        assert indexed_count == len(sample_docs)
    
    def test_collection_stats(self, indexer):
        """Test getting collection statistics"""
        stats = indexer.get_collection_stats()
        
        assert "collection_name" in stats
        assert "total_documents" in stats
        assert isinstance(stats["total_documents"], int)
    
    def test_clear_collection(self, indexer):
        """Test clearing collection"""
        # First add some documents
        sample_docs = [
            Document(page_content="Test document", metadata={"chunk_id": "test"})
        ]
        sample_embeddings = [[0.1, 0.2, 0.3] * 100]
        indexer.index_documents(sample_docs, sample_embeddings)
        
        # Clear collection
        indexer.clear_collection()
        
        # Verify empty
        stats = indexer.get_collection_stats()
        assert stats["total_documents"] == 0


class TestRAGPipeline:
    """Integration tests for complete RAG pipeline"""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        from src.processing.pipeline import MedicalRAGPipeline
        
        pipeline = MedicalRAGPipeline(
            data_dir="./data/raw",
            collection_name="test_pipeline"
        )
        
        assert pipeline.loader is not None
        assert pipeline.chunker is not None
        assert pipeline.embedder is not None
        assert pipeline.indexer is not None
    
    def test_pipeline_with_sample_data(self):
        """Test pipeline with sample data"""
        from src.processing.pipeline import MedicalRAGPipeline
        
        pipeline = MedicalRAGPipeline(
            data_dir="./data/raw",
            collection_name="test_pipeline_sample"
        )
        
        # Run pipeline with sample data
        stats = pipeline.run_pipeline(load_sample=True, save_results=False)
        
        assert stats["documents_loaded"] > 0
        assert stats["chunks_after_filtering"] > 0
        assert stats["documents_indexed"] > 0
        assert "embedding_dim" in stats


class TestRAGQuality:
    """Tests for RAG data quality"""
    
    def test_no_empty_chunks(self):
        """Test that no chunks are empty"""
        chunker = MedicalTextChunker()
        
        sample_doc = Document(
            page_content="Valid medical text about cardiovascular health.",
            metadata={"source": "test"}
        )
        
        chunks = chunker.chunk_documents([sample_doc])
        
        # No empty chunks
        assert all(chunk.page_content.strip() for chunk in chunks)
    
    def test_metadata_completeness(self):
        """Test that required metadata fields are present"""
        chunker = MedicalTextChunker()
        
        sample_doc = Document(
            page_content="Medical text about diabetes management.",
            metadata={"source": "test_doc"}
        )
        
        chunks = chunker.chunk_documents([sample_doc])
        
        required_fields = ["chunk_id", "chunk_index", "total_chunks"]
        
        for chunk in chunks:
            assert all(field in chunk.metadata for field in required_fields)
    
    def test_chunk_size_distribution(self):
        """Test that chunk sizes are reasonably distributed"""
        chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        
        # Create a longer document
        long_text = "Medical text about cardiology. " * 100
        sample_doc = Document(page_content=long_text, metadata={"source": "test"})
        
        chunks = chunker.chunk_documents([sample_doc])
        stats = chunker.analyze_chunks(chunks)
        
        # Check statistics are reasonable
        assert stats["avg_length"] > 0
        assert stats["max_length"] <= chunker.chunk_size + chunker.chunk_overlap
        assert stats["min_length"] >= 50  # After filtering


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

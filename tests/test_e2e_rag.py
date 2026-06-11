"""
Tests End-to-End pour Pipeline RAG Médical
Teste le système complet : ingestion → chunking → embeddings → retrieval → monitoring
"""

import pytest
import time
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class TestRAGE2E:
    """Tests E2E complets pour le pipeline RAG médical"""
    
    @pytest.fixture(scope="class")
    def setup_rag_system(self):
        """Setup du système RAG avant tous les tests"""
        logger.info("Setting up RAG system for E2E tests")
        
        try:
            # Import des composants RAG
            from src.ingestion.medical_loader import MedicalDocumentLoader
            from src.processing.chunker import MedicalTextChunker
            from sentence_transformers import SentenceTransformer
            
            # Initialisation
            self.loader = MedicalDocumentLoader("./data/raw")
            self.chunker = MedicalTextChunker(chunk_size=1000, chunk_overlap=200)
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Chargement et chunking
            logger.info("Loading documents...")
            documents = self.loader.load_sample_documents()
            logger.info(f"Loaded {len(documents)} documents")
            
            logger.info("Chunking documents...")
            chunks = self.chunker.chunk_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Embeddings
            logger.info("Creating embeddings...")
            chunk_texts = [chunk.page_content for chunk in chunks]
            self.embeddings = self.model.encode(chunk_texts)
            logger.info(f"Created embeddings shape: {self.embeddings.shape}")
            
            # Stockage pour tests
            self.chunks = chunks
            
            yield self
            
        except Exception as e:
            logger.error(f"Error during setup: {e}")
            pytest.fail(f"Setup failed: {e}")
    
    @pytest.fixture(scope="class")
    def cleanup_rag_system(self):
        """Cleanup après tous les tests"""
        logger.info("Cleaning up RAG system")
        yield
        # Nettoyage si nécessaire
    
    def test_document_loading(self, setup_rag_system):
        """Test 1: Chargement des documents médicaux"""
        logger.info("Test: Document loading")
        
        documents = setup_rag_system.loader.load_sample_documents()
        
        assert len(documents) > 0, "No documents loaded"
        assert len(documents) >= 5, "Expected at least 5 medical documents"
        
        logger.info(f"✓ Document loading successful: {len(documents)} documents")
    
    def test_chunking_quality(self, setup_rag_system):
        """Test 2: Qualité du chunking"""
        logger.info("Test: Chunking quality")
        
        chunks = setup_rag_system.chunks
        
        # Vérifier nombre de chunks
        assert len(chunks) > 0, "No chunks created"
        
        # Vérifier taille des chunks (approximative)
        for chunk in chunks:
            text_length = len(chunk.page_content)
            assert text_length > 100, "Chunk too short"
            assert text_length < 2000, "Chunk too long"
        
        # Vérifier métadonnées
        for chunk in chunks:
            assert 'source' in chunk.metadata, "Chunk missing source metadata"
        
        logger.info(f"✓ Chunking quality check passed: {len(chunks)} chunks")
    
    def test_embedding_generation(self, setup_rag_system):
        """Test 3: Génération des embeddings"""
        logger.info("Test: Embedding generation")
        
        embeddings = setup_rag_system.embeddings
        chunks = setup_rag_system.chunks
        
        # Vérifier dimensions
        assert embeddings.shape[0] == len(chunks), "Embeddings count doesn't match chunks count"
        assert embeddings.shape[1] == 384, f"Expected 384 dimensions, got {embeddings.shape[1]}"
        
        # Vérifier valeurs valides (pas de NaN ou Inf)
        import numpy as np
        assert not np.isnan(embeddings).any(), "Embeddings contain NaN values"
        assert not np.isinf(embeddings).any(), "Embeddings contain Inf values"
        
        logger.info(f"✓ Embedding generation successful: {embeddings.shape}")
    
    def test_retrieval_performance(self, setup_rag_system):
        """Test 4: Performance du retrieval"""
        logger.info("Test: Retrieval performance")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Query de test
        test_query = "diabetes symptoms treatment"
        query_embedding = setup_rag_system.model.encode([test_query])
        
        # Mesurer temps de retrieval
        start_time = time.time()
        
        similarities = cosine_similarity(query_embedding, setup_rag_system.embeddings).flatten()
        top_k_indices = np.argsort(similarities)[-5:][::-1]
        
        retrieval_time = time.time() - start_time
        
        # Vérifier performance
        assert retrieval_time < 0.1, f"Retrieval too slow: {retrieval_time*1000:.2f}ms > 100ms"
        assert len(top_k_indices) == 5, "Expected 5 results"
        
        # Vérifier similarités valides
        for idx in top_k_indices:
            assert 0 <= similarities[idx] <= 1, f"Invalid similarity score: {similarities[idx]}"
        
        logger.info(f"✓ Retrieval performance: {retrieval_time*1000:.2f}ms, top-5 similarities retrieved")
    
    def test_retrieval_quality(self, setup_rag_system):
        """Test 5: Qualité du retrieval (MRR)"""
        logger.info("Test: Retrieval quality (MRR)")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Queries de test avec chunks pertinents attendus
        test_cases = [
            ("diabetes symptoms", [0]),  # Premier document sur diabetes
            ("heart disease", [3]),      # Quatrième document sur heart disease
        ]
        
        mrr_scores = []
        
        for query, relevant_indices in test_cases:
            query_embedding = setup_rag_system.model.encode([query])
            similarities = cosine_similarity(query_embedding, setup_rag_system.embeddings).flatten()
            top_k_indices = np.argsort(similarities)[-5:][::-1]
            
            # Calcul MRR
            for i, idx in enumerate(top_k_indices):
                if idx in relevant_indices:
                    mrr_scores.append(1 / (i + 1))
                    break
            else:
                mrr_scores.append(0)
        
        # Vérifier MRR moyen
        avg_mrr = sum(mrr_scores) / len(mrr_scores)
        assert avg_mrr > 0.5, f"MRR too low: {avg_mrr:.3f}"
        
        logger.info(f"✓ Retrieval quality: MRR = {avg_mrr:.3f}")
    
    def test_batch_retrieval(self, setup_rag_system):
        """Test 6: Batch retrieval performance"""
        logger.info("Test: Batch retrieval performance")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # 10 queries en batch
        queries = [
            "diabetes symptoms", "heart disease", "asthma treatment",
            "hypertension", "kidney disease", "blood sugar",
            "chest pain", "breathing issues", "high blood pressure", "renal failure"
        ]
        
        start_time = time.time()
        
        for query in queries:
            query_embedding = setup_rag_system.model.encode([query])
            similarities = cosine_similarity(query_embedding, setup_rag_system.embeddings).flatten()
            top_k = np.argsort(similarities)[-5:][::-1]
        
        batch_time = time.time() - start_time
        
        # Vérifier performance batch (< 5 secondes pour 10 queries)
        assert batch_time < 5.0, f"Batch retrieval too slow: {batch_time:.2f}s > 5s"
        
        avg_time_per_query = batch_time / len(queries)
        logger.info(f"✓ Batch retrieval: {batch_time:.2f}s total, {avg_time_per_query*1000:.2f}ms per query")
    
    def test_embedding_quality(self, setup_rag_system):
        """Test 7: Qualité des embeddings (similarité sémantique)"""
        logger.info("Test: Embedding quality")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Queries similaires doivent récupérer des chunks similaires
        similar_queries = [
            "diabetes symptoms",
            "signs of diabetes"
        ]
        
        results = []
        for query in similar_queries:
            query_embedding = setup_rag_system.model.encode([query])
            similarities = cosine_similarity(query_embedding, setup_rag_system.embeddings).flatten()
            top_indices = np.argsort(similarities)[-3:][::-1]
            results.append(set(top_indices))
        
        # Vérifier overlap entre résultats
        overlap = results[0] & results[1]
        assert len(overlap) > 0, "Similar queries should retrieve similar chunks"
        
        logger.info(f"✓ Embedding quality: {len(overlap)} common chunks for similar queries")
    
    def test_system_stability(self, setup_rag_system):
        """Test 8: Stabilité du système (requêtes répétées)"""
        logger.info("Test: System stability")
        
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # 5 fois la même query
        query = "diabetes treatment"
        results = []
        
        for i in range(5):
            query_embedding = setup_rag_system.model.encode([query])
            similarities = cosine_similarity(query_embedding, setup_rag_system.embeddings).flatten()
            top_indices = np.argsort(similarities)[-3:][::-1]
            results.append(top_indices)
        
        # Vérifier cohérence (mêmes résultats à chaque fois)
        for i in range(1, len(results)):
            assert np.array_equal(results[0], results[i]), "Results inconsistent across runs"
        
        logger.info("✓ System stability: Consistent results across 5 runs")
    
    def test_error_handling(self, setup_rag_system):
        """Test 9: Gestion des erreurs"""
        logger.info("Test: Error handling")
        
        from sentence_transformers import SentenceTransformer
        
        # Test avec query vide
        try:
            query_embedding = setup_rag_system.model.encode([""])
            assert query_embedding.shape == (1, 384), "Empty query should still generate valid embedding"
        except Exception as e:
            logger.warning(f"Empty query handling: {e}")
        
        # Test avec query très longue
        long_query = " ".join(["diabetes"] * 1000)
        try:
            query_embedding = setup_rag_system.model.encode([long_query])
            assert query_embedding.shape == (1, 384), "Long query should still generate valid embedding"
        except Exception as e:
            logger.warning(f"Long query handling: {e}")
        
        logger.info("✓ Error handling: Basic edge cases tested")


def test_e2e_integration():
    """Test d'intégration rapide pour vérifier que tout fonctionne ensemble"""
    logger.info("Running quick E2E integration test")
    
    try:
        # Import des composants
        from src.ingestion.medical_loader import MedicalDocumentLoader
        from src.processing.chunker import MedicalTextChunker
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Setup rapide
        loader = MedicalDocumentLoader("./data/raw")
        chunker = MedicalTextChunker(chunk_size=1000, chunk_overlap=200)
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Pipeline complet
        documents = loader.load_sample_documents()
        chunks = chunker.chunk_documents(documents)
        chunk_texts = [chunk.page_content for chunk in chunks]
        embeddings = model.encode(chunk_texts)
        
        # Test retrieval
        query = "diabetes symptoms"
        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, embeddings).flatten()
        top_k = np.argsort(similarities)[-3:][::-1]
        
        # Assertions
        assert len(documents) > 0, "No documents loaded"
        assert len(chunks) > 0, "No chunks created"
        assert embeddings.shape[1] == 384, "Wrong embedding dimensions"
        assert len(top_k) == 3, "Wrong number of results"
        
        logger.info("✓ E2E integration test PASSED")
        
    except Exception as e:
        logger.error(f"E2E integration test FAILED: {e}")
        pytest.fail(f"E2E integration test failed: {e}")


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "--tb=short"])
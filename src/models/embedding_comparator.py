"""
Embedding Model Comparator for Medical RAG
Compares different sentence-transformer models for medical domain
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class EmbeddingModelComparator:
    """Compare different embedding models for medical RAG"""
    
    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
        
    def add_model(self, model_name: str, model_path: str):
        """
        Ajouter un modèle à comparer
        
        Args:
            model_name: Nom du modèle
            model_path: Path HuggingFace du modèle
        """
        self.logger.info(f"Loading embedding model: {model_path}")
        try:
            model = SentenceTransformer(model_path)
            self.models[model_name] = {
                'model': model,
                'embedding_dim': model.get_sentence_embedding_dimension(),
                'model_path': model_path
            }
            self.logger.info(f"Model {model_name} loaded: {model.get_sentence_embedding_dimension()} dimensions")
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            raise
        
    def compare_models(self, chunks: List[Document], test_queries: List[tuple[str, List[int]]]) -> List[Dict[str, Any]]:
        """
        Comparer plusieurs embedding models sur retrieval quality
        
        Args:
            chunks: List of chunked Document objects
            test_queries: List of (query, relevant_chunk_ids) tuples
            
        Returns:
            List of comparison results per model
        """
        self.logger.info(f"Comparing {len(self.models)} embedding models")
        
        results = []
        
        for model_name, model_info in self.models.items():
            self.logger.info(f"Testing model: {model_name}")
            model = model_info['model']
            
            # Generate embeddings
            chunk_texts = [chunk.page_content for chunk in chunks]
            self.logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
            
            try:
                chunk_embeddings = model.encode(chunk_texts, show_progress_bar=False)
                self.logger.info(f"Generated embeddings shape: {chunk_embeddings.shape}")
                
                # Test retrieval quality
                mrr_scores = []
                retrieval_times = []
                
                self.logger.info(f"Testing with {len(test_queries)} queries")
                for query_idx, (query, relevant_ids) in enumerate(test_queries):
                    self.logger.info(f"Query {query_idx}: '{query}', relevant indices: {relevant_ids}")
                    import time
                    start = time.time()
                    
                    query_embedding = model.encode([query])
                    similarities = cosine_similarity(query_embedding, chunk_embeddings).flatten()
                    top_k_indices = np.argsort(similarities)[-5:][::-1]
                    
                    end = time.time()
                    retrieval_times.append((end - start) * 1000)
                    
                    self.logger.info(f"Top 5 indices: {top_k_indices}")
                    
                    # MRR calculation
                    for i, idx in enumerate(top_k_indices):
                        if idx in relevant_ids:
                            mrr_scores.append(1 / (i + 1))
                            self.logger.info(f"Found relevant at rank {i+1}, MRR contribution: {1/(i+1)}")
                            break
                    else:
                        mrr_scores.append(0)
                        self.logger.info("No relevant chunk found in top 5")
                
                model_result = {
                    'Model': model_name,
                    'Embedding Dim': model_info['embedding_dim'],
                    'Model Path': model_info['model_path'],
                    'MRR': np.mean(mrr_scores),
                    'Avg Retrieval Time (ms)': np.mean(retrieval_times),
                    'Total Chunks': len(chunks),
                    'Model_Object': model
                }
                
                results.append(model_result)
                self.logger.info(f"Model {model_name}: MRR={model_result['MRR']:.3f}, Time={model_result['Avg Retrieval Time (ms)']:.2f}ms")
                
            except Exception as e:
                self.logger.error(f"Error testing model {model_name}: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                continue
        
        return results
    
    def select_best_model(self, results: List[Dict[str, Any]], metric: str = 'MRR') -> Dict[str, Any]:
        """
        Sélectionner le meilleur modèle selon la métrique
        
        Args:
            results: List of model comparison results
            metric: Metric to use for selection ('MRR' or 'Avg Retrieval Time (ms)')
            
        Returns:
            Dictionary with best model info
        """
        if metric == 'MRR':
            # Higher is better
            best = max(results, key=lambda x: x[metric])
        else:
            # Lower is better for time
            best = min(results, key=lambda x: x[metric])
        
        self.logger.info(f"Best model selected: {best['Model']} ({metric}: {best[metric]})")
        return best
    
    def create_comparison_table(self, results: List[Dict[str, Any]]) -> str:
        """
        Créer un tableau comparatif formaté
        
        Args:
            results: List of model comparison results
            
        Returns:
            Formatted comparison table string
        """
        table = f"{'Model':<30} | {'Dim':<6} | {'MRR':<8} | {'Time (ms)':<12}\n"
        table += "-" * 70 + "\n"
        
        for result in results:
            table += f"{result['Model']:<30} | {result['Embedding Dim']:<6} | {result['MRR']:.3f} | {result['Avg Retrieval Time (ms)']:.2f}\n"
        
        return table


def create_test_queries_medical(chunks: List[Document]) -> List[tuple[str, List[int]]]:
    """
    Créer des queries médicales de test
    
    Args:
        chunks: List of chunked Document objects
        
    Returns:
        List of (query, relevant_chunk_indices) tuples
    """
    # Dynamic test queries based on actual chunk content
    medical_queries = []
    
    for i, chunk in enumerate(chunks):
        content_lower = chunk.page_content.lower()
        
        # Generate a query based on chunk content keywords
        if 'diabetes' in content_lower:
            medical_queries.append(("diabetes symptoms treatment", [i]))
        elif 'hypertension' in content_lower or 'blood pressure' in content_lower:
            medical_queries.append(("hypertension high blood pressure", [i]))
        elif 'asthma' in content_lower or 'wheezing' in content_lower:
            medical_queries.append(("asthma wheezing treatment", [i]))
        elif 'heart' in content_lower or 'cardiovascular' in content_lower:
            medical_queries.append(("heart disease prevention", [i]))
        elif 'kidney' in content_lower or 'renal' in content_lower:
            medical_queries.append(("kidney disease chronic", [i]))
    
    # Ensure we have at least some queries
    if not medical_queries:
        # Fallback: simple queries for first chunks
        for i in range(min(3, len(chunks))):
            medical_queries.append((f"query_{i}", [i]))
    
    return medical_queries


def main():
    """Main function to test embedding comparison"""
    from src.processing.chunker import MedicalTextChunker
    from src.ingestion.medical_loader import MedicalDocumentLoader
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load and chunk documents
    loader = MedicalDocumentLoader()
    documents = loader.load_sample_documents()
    chunker = MedicalTextChunker()
    chunks = chunker.chunk_documents(documents)
    
    print(f"\nLoaded {len(chunks)} chunks")
    
    # Create test queries
    test_queries = create_test_queries_medical(chunks)
    print(f"Created {len(test_queries)} test queries")
    
    # Add models to compare
    comparator = EmbeddingModelComparator()
    
    # Note: Using smaller models for faster testing
    # In production, use: "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
    try:
        print("Adding MiniLM-L6-v2 model...")
        comparator.add_model("MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2")
        print("Model added successfully")
    except Exception as e:
        print(f"Warning: Failed to load MiniLM-L6-v2: {e}")
        return
    
    # Compare models
    try:
        print("Starting model comparison...")
        results = comparator.compare_models(chunks, test_queries)
        print(f"Comparison completed, got {len(results)} results")
    except Exception as e:
        print(f"Error during comparison: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if results:
        print("\n" + "=" * 70)
        print("EMBEDDING MODEL COMPARISON:")
        print("=" * 70)
        print(comparator.create_comparison_table(results))
        
        best = comparator.select_best_model(results, metric='MRR')
        print(f"\n✓ Best model: {best['Model']} (MRR: {best['MRR']:.3f})")
    else:
        print("No models successfully compared")


if __name__ == "__main__":
    main()

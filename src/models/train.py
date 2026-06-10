"""
Medical RAG Training Pipeline
Orchestrates embedding model comparison, chunking experiments, and MLflow tracking
"""

import mlflow
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
from src.models.baseline import RAGBaseline, create_test_queries
from src.models.embedding_comparator import EmbeddingModelComparator, create_test_queries_medical

logger = logging.getLogger(__name__)

class MedicalRAGTrainer:
    """Complete RAG training pipeline with MLflow tracking"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Medical RAG Training Pipeline")
        
        # Initialize components
        self.loader = MedicalDocumentLoader(data_dir)
        self.chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        self.embedding_comparator = EmbeddingModelComparator()
        
        # Setup MLflow
        mlflow.set_experiment("medical_rag_experiments")
        
    def run_baseline_experiments(self):
        """Run baseline RAG experiments"""
        self.logger.info("=" * 60)
        self.logger.info("Running Baseline RAG Experiments")
        self.logger.info("=" * 60)
        
        # Load and chunk documents
        documents = self.loader.load_sample_documents()
        chunks = self.chunker.chunk_documents(documents)
        test_queries = create_test_queries(chunks)
        
        baseline_results = {}
        
        # Test TF-IDF baseline
        with mlflow.start_run(run_name="baseline_tfidf"):
            mlflow.log_params({'baseline_type': 'tfidf', 'max_features': 1000})
            
            tfidf_baseline = RAGBaseline(retrieval_type='tfidf')
            tfidf_baseline.fit(chunks)
            results = tfidf_baseline.evaluate(test_queries)
            
            mlflow.log_metrics(results)
            baseline_results['tfidf'] = results
            
            self.logger.info(f"TF-IDF Baseline: MRR={results['mean_reciprocal_rank']:.3f}")
        
        # Test Random baseline
        with mlflow.start_run(run_name="baseline_random"):
            mlflow.log_params({'baseline_type': 'random'})
            
            random_baseline = RAGBaseline(retrieval_type='random')
            random_baseline.fit(chunks)
            results = random_baseline.evaluate(test_queries)
            
            mlflow.log_metrics(results)
            baseline_results['random'] = results
            
            self.logger.info(f"Random Baseline: MRR={results['mean_reciprocal_rank']:.3f}")
        
        return baseline_results
    
    def run_embedding_comparison(self, chunks: List[Document], test_queries: List[tuple[str, List[str]]]):
        """Run embedding model comparison"""
        self.logger.info("=" * 60)
        self.logger.info("Running Embedding Model Comparison")
        self.logger.info("=" * 60)
        
        # Add models to compare
        # Using lightweight models for testing
        try:
            self.embedding_comparator.add_model("MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2")
        except Exception as e:
            self.logger.warning(f"Failed to load MiniLM: {e}")
        
        # Compare models
        comparison_results = []
        
        for model_name in list(self.embedding_comparator.models.keys()):
            with mlflow.start_run(run_name=f"embedding_{model_name}"):
                model_info = self.embedding_comparator.models[model_name]
                
                mlflow.log_params({
                    'model_name': model_name,
                    'embedding_dim': model_info['embedding_dim'],
                    'model_path': model_info['model_path']
                })
                
                # Test with subset of models
                try:
                    model_results = self.embedding_comparator.compare_models(
                        {model_name: model_info},
                        chunks,
                        test_queries
                    )
                    
                    if model_results:
                        result = model_results[0]
                        mlflow.log_metrics({
                            'mrr': result['MRR'],
                            'avg_retrieval_time_ms': result['Avg Retrieval Time (ms)']
                        })
                        comparison_results.extend(model_results)
                        
                except Exception as e:
                    self.logger.error(f"Error testing model {model_name}: {e}")
        
        return comparison_results
    
    def run_chunking_experiments(self, documents: List[Document], embedding_model_name: str):
        """Run chunking strategy experiments"""
        self.logger.info("=" * 60)
        self.logger.info("Running Chunking Strategy Experiments")
        self.logger.info("=" * 60)
        
        chunk_strategies = [
            {'name': 'small_chunks', 'chunk_size': 256, 'chunk_overlap': 25},
            {'name': 'medium_chunks', 'chunk_size': 512, 'chunk_overlap': 50},
            {'name': 'large_chunks', 'chunk_size': 1024, 'chunk_overlap': 100}
        ]
        
        chunking_results = []
        
        for strategy in chunk_strategies:
            with mlflow.start_run(run_name=f"chunking_{strategy['name']}"):
                mlflow.log_params(strategy)
                
                # Chunk with strategy
                chunker = MedicalTextChunker(
                    chunk_size=strategy['chunk_size'],
                    chunk_overlap=strategy['chunk_overlap']
                )
                chunks = chunker.chunk_documents(documents)
                
                # Calculate stats
                chunk_lengths = [len(c.page_content) for c in chunks]
                
                mlflow.log_metrics({
                    'num_chunks': len(chunks),
                    'avg_chunk_length': np.mean(chunk_lengths),
                    'min_chunk_length': min(chunk_lengths),
                    'max_chunk_length': max(chunk_lengths)
                })
                
                result = {
                    'strategy': strategy['name'],
                    'num_chunks': len(chunks),
                    'avg_length': np.mean(chunk_lengths),
                    'chunks': chunks
                }
                chunking_results.append(result)
                
                self.logger.info(f"Strategy {strategy['name']}: {len(chunks)} chunks")
        
        return chunking_results
    
    def save_results(self, baseline_results: Dict, embedding_results: List, 
                     chunking_results: List, output_dir: str = "./data/processed"):
        """Save all training results"""
        results_path = Path(output_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save baseline results
        baseline_file = results_path / f"baseline_results_{timestamp}.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline_results, f, indent=2)
        
        # Save embedding comparison
        embedding_file = results_path / f"embedding_comparison_{timestamp}.json"
        with open(embedding_file, 'w') as f:
            json.dump(embedding_results, f, indent=2)
        
        # Save chunking results
        chunking_file = results_path / f"chunking_results_{timestamp}.json"
        with open(chunking_file, 'w') as f:
            json.dump(chunking_results, f, indent=2)
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'baseline_results': baseline_results,
            'embedding_comparison': [
                {
                    'Model': r['Model'],
                    'MRR': r['MRR'],
                    'Time_ms': r['Avg Retrieval Time (ms)']
                } for r in embedding_results
            ],
            'chunking_strategies': [
                {
                    'Strategy': r['strategy'],
                    'Num_chunks': r['num_chunks'],
                    'Avg_length': r['avg_length']
                } for r in chunking_results
            ]
        }
        
        summary_file = results_path / f"training_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Results saved to {results_path}")
    
    def run_complete_training(self):
        """Run complete RAG training pipeline"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING COMPLETE RAG TRAINING PIPELINE")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Baseline experiments
            baseline_results = self.run_baseline_experiments()
            
            # Step 2: Load documents for other experiments
            documents = self.loader.load_sample_documents()
            chunks = self.chunker.chunk_documents(documents)
            test_queries = create_test_queries_medical(chunks)
            
            # Step 3: Embedding comparison
            embedding_results = self.run_embedding_comparison(chunks, test_queries)
            
            # Step 4: Chunking experiments
            chunking_results = self.run_chunking_experiments(documents, "MiniLM-L6-v2")
            
            # Step 5: Save results
            self.save_results(baseline_results, embedding_results, chunking_results)
            
            self.logger.info("=" * 60)
            self.logger.info("RAG TRAINING PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 60)
            
            # Print summary
            print("\n" + "=" * 60)
            print("TRAINING SUMMARY:")
            print("=" * 60)
            print(f"Baselines: {list(baseline_results.keys())}")
            print(f"Embeddings tested: {len(embedding_results)}")
            print(f"Chunking strategies: {len(chunking_results)}")
            print("Results saved to data/processed/")
            
            return {
                'baseline_results': baseline_results,
                'embedding_results': embedding_results,
                'chunking_results': chunking_results
            }
            
        except Exception as e:
            self.logger.error(f"Training pipeline failed: {e}")
            raise


def main():
    """Main function to run RAG training"""
    logging.basicConfig(level=logging.INFO)
    
    trainer = MedicalRAGTrainer(data_dir="./data/raw")
    results = trainer.run_complete_training()
    
    return results


if __name__ == "__main__":
    main()

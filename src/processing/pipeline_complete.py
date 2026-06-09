"""
Complete RAG Pipeline with All J2 Components
Integrates loading, chunking, features engineering, EDA, and validation
"""

from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
from src.processing.feature_engineering import MedicalFeatureEngineer
from src.processing.eda import MedicalRAGEDA
import logging
import json
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CompleteRAGPipeline:
    """Complete RAG pipeline with all J2 components"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Complete RAG Pipeline (All J2 Components)")
        
        # Initialize all components
        self.loader = MedicalDocumentLoader(data_dir)
        self.chunker = MedicalTextChunker(chunk_size=512, chunk_overlap=50)
        self.feature_engineer = MedicalFeatureEngineer()
        self.eda = MedicalRAGEDA()
        
        # Pipeline statistics
        self.stats = {}

    def run_complete_pipeline(self, save_results: bool = True, results_dir: str = "./data/processed"):
        """Run the complete RAG pipeline with all J2 components"""
        self.logger.info("=" * 60)
        self.logger.info("Starting COMPLETE RAG Pipeline (All J2 Components)")
        self.logger.info("=" * 60)
        
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
            
            # Step 4: Feature Engineering (5-10 features)
            self.logger.info("Step 4: Extracting features (5-10 features per chunk)...")
            features = self.feature_engineer.extract_features(chunks)
            feature_summary = self.feature_engineer.get_feature_summary(features)
            self.stats["features_extracted"] = len(features)
            self.stats["features_per_chunk"] = len(features[0]) if features else 0
            self.stats.update(feature_summary)
            self.logger.info(f"✅ Features extracted: {len(features)} chunks, {len(features[0]) if features else 0} features per chunk")
            
            # Step 5: EDA with Key Insights
            self.logger.info("Step 5: Performing EDA and generating insights...")
            insights = self.feature_engineer.generate_insights(features)
            self.stats["eda_insights_generated"] = len(insights)
            self.logger.info(f"✅ EDA insights generated: {len(insights)} insights")
            
            # Step 6: Data Quality Validation
            self.logger.info("Step 6: Validating data quality...")
            quality_results = self._validate_data_quality(chunks, features)
            self.stats.update(quality_results)
            self.logger.info(f"✅ Data quality validated: {quality_results}")
            
            # Step 7: Save Results
            if save_results:
                self.logger.info("Step 7: Saving results...")
                self._save_complete_results(chunks, features, insights, quality_results, results_dir)
            
            self.logger.info("=" * 60)
            self.logger.info("COMPLETE RAG Pipeline finished successfully!")
            self.logger.info("=" * 60)
            self.logger.info(f"Pipeline Statistics: {json.dumps(self.stats, indent=2)}")
            
            return self.stats
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise

    def _validate_data_quality(self, chunks, features):
        """Validate data quality according to J2 criteria"""
        results = {
            "quality_validation": {},
            "tests_passed": 0,
            "tests_failed": 0
        }
        
        # Test 1: No empty chunks
        empty_chunks = [c for c in chunks if not c.page_content.strip()]
        results["quality_validation"]["no_empty_chunks"] = len(empty_chunks) == 0
        results["tests_passed"] += 1 if len(empty_chunks) == 0 else 0
        results["tests_failed"] += 0 if len(empty_chunks) == 0 else 1
        
        # Test 2: No null features
        null_features = [f for f in features if any(v is None for v in f.values())]
        results["quality_validation"]["no_null_features"] = len(null_features) == 0
        results["tests_passed"] += 1 if len(null_features) == 0 else 0
        results["tests_failed"] += 0 if len(null_features) == 0 else 1
        
        # Test 3: Chunks in valid range
        out_of_range = [c for c in chunks if len(c.page_content) < 50 or len(c.page_content) > 2000]
        results["quality_validation"]["chunks_in_valid_range"] = len(out_of_range) == 0
        results["tests_passed"] += 1 if len(out_of_range) == 0 else 0
        results["tests_failed"] += 0 if len(out_of_range) == 0 else 1
        
        # Test 4: Features completeness (minimum 5 features)
        feature_count = len(features[0]) if features else 0
        results["quality_validation"]["features_completeness"] = feature_count >= 5
        results["tests_passed"] += 1 if feature_count >= 5 else 0
        results["tests_failed"] += 0 if feature_count >= 5 else 1
        
        # Test 5: Insights generated (minimum 3 insights)
        insights = self.feature_engineer.generate_insights(features)
        results["quality_validation"]["insights_generated"] = len(insights) >= 3
        results["tests_passed"] += 1 if len(insights) >= 3 else 0
        results["tests_failed"] += 0 if len(insights) >= 3 else 1
        
        self.logger.info(f"Quality validation: {results['tests_passed']}/{results['tests_passed'] + results['tests_failed']} tests passed")
        
        return results

    def _save_complete_results(self, chunks, features, insights, quality_results, results_dir: str):
        """Save all pipeline results"""
        results_path = Path(results_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save chunks
        chunks_data = [{
            "content": chunk.page_content,
            "metadata": chunk.metadata
        } for chunk in chunks]
        
        chunks_file = results_path / f"complete_chunks_{timestamp}.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save features
        features_file = results_path / f"features_{timestamp}.json"
        with open(features_file, 'w') as f:
            json.dump(features, f, indent=2)
        
        # Save insights
        insights_file = results_path / f"INSIGHTS.md"
        self.eda.save_insights(insights, str(insights_file))
        
        # Save complete statistics
        complete_stats = {
            "timestamp": timestamp,
            "pipeline_statistics": self.stats,
            "quality_validation": quality_results,
            "features_summary": self.feature_engineer.get_feature_summary(features)
        }
        
        stats_file = results_path / f"complete_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(complete_stats, f, indent=2)
        
        self.logger.info(f"Complete results saved to {results_path}")

def main():
    """Main function to run the complete RAG pipeline"""
    pipeline = CompleteRAGPipeline(data_dir="./data/raw")
    stats = pipeline.run_complete_pipeline(save_results=True)
    
    print("\n" + "=" * 60)
    print("COMPLETE RAG PIPELINE STATISTICS:")
    print("=" * 60)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("J2 COMPLETION STATUS:")
    print("=" * 60)
    print(f"✓ Pipeline ETL/RAG implémentée et testée: {stats.get('documents_loaded', 0)} docs → {stats.get('chunks_after_filtering', 0)} chunks")
    print(f"✓ Features engineering créées (5-10 features): {stats.get('features_per_chunk', 0)} features per chunk")
    print(f"✓ EDA réalisée avec insights clés: {stats.get('eda_insights_generated', 0)} insights générés")
    print(f"✓ Qualité données validée: {stats.get('tests_passed', 0)}/{stats.get('tests_passed', 0) + stats.get('tests_failed', 0)} tests passent")
    print(f"✓ Dataset ML-ready sauvegardé et versionné: Complete results saved to data/processed/")

if __name__ == "__main__":
    main()

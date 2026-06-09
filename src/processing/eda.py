"""
Medical RAG EDA
Exploratory Data Analysis for medical documents and chunks
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MedicalRAGEDA:
    """Exploratory Data Analysis for medical RAG data"""
    
    def __init__(self, data_dir: str = "./data/processed"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
    def analyze_chunks_file(self, chunks_file: str) -> Dict[str, Any]:
        """
        Analyze chunks from JSON file
        
        Args:
            chunks_file: Path to chunks JSON file
            
        Returns:
            Dictionary with EDA statistics
        """
        self.logger.info(f"Analyzing chunks from {chunks_file}")
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        # Basic statistics
        total_chunks = len(chunks_data)
        lengths = [chunk['metadata']['chunk_length'] for chunk in chunks_data]
        chunk_types = [chunk['metadata'].get('chunk_type', 'unknown') for chunk in chunks_data]
        
        # Calculate statistics
        stats = {
            "total_chunks": total_chunks,
            "avg_length": sum(lengths) / len(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "median_length": sorted(lengths)[len(lengths) // 2] if lengths else 0,
            "chunk_type_distribution": {}
        }
        
        # Count chunk types
        for chunk_type in chunk_types:
            stats["chunk_type_distribution"][chunk_type] = stats["chunk_type_distribution"].get(chunk_type, 0) + 1
        
        # Content analysis
        all_text = " ".join(chunk['content'] for chunk in chunks_data)
        total_words = len(all_text.split())
        unique_words = len(set(all_text.lower().split()))
        
        stats["total_words"] = total_words
        stats["unique_words"] = unique_words
        stats["vocabulary_richness"] = unique_words / total_words if total_words > 0 else 0
        
        self.logger.info(f"EDA Statistics: {stats}")
        return stats
    
    def generate_insights(self, stats: Dict[str, Any]) -> List[str]:
        """
        Generate narrative insights from statistics
        
        Args:
            stats: Dictionary with EDA statistics
            
        Returns:
            List of narrative insight strings
        """
        insights = []
        
        # Insight 1: Chunk distribution
        insights.append(f"Nous avons découvert que le corpus médical contient {stats['total_chunks']} chunks "
                       f"avec une longueur moyenne de {stats['avg_length']:.1f} caractères, "
                       f"ce qui suggère une segmentation {'fine' if stats['avg_length'] < 300 else 'moyenne'} du contenu.")
        
        # Insight 2: Content richness
        if stats['vocabulary_richness'] > 0.6:
            insights.append(f"Le vocabulaire médical montre une richesse de {stats['vocabulary_richness']:.2f}, "
                           f"indiquant une diversité terminologique importante ({stats['unique_words']} mots uniques sur {stats['total_words']} mots totaux).")
        else:
            insights.append(f"Le vocabulaire montre une richesse de {stats['vocabulary_richness']:.2f}, "
                           f"suggérant une répétition terminologique qui pourrait indiquer un contenu technique spécialisé.")
        
        # Insight 3: Category distribution
        if stats['chunk_type_distribution']:
            most_common = max(stats['chunk_type_distribution'].items(), key=lambda x: x[1])
            insights.append(f"La catégorie médicale dominante est '{most_common[0]}' avec {most_common[1]} chunks "
                           f"({most_common[1]/stats['total_chunks']*100:.1f}% du corpus), "
                           f"ce qui indique une orientation {'clinique' if most_common[0] in ['symptoms', 'treatment'] else 'générale'} du contenu.")
        
        # Insight 4: Length variance
        if stats['max_length'] - stats['min_length'] > 500:
            insights.append(f"La variance des longueurs de chunks est significative (min: {stats['min_length']}, max: {stats['max_length']}), "
                           f"ce qui pourrait affecter la qualité des embeddings et nécessiter un ajustement de la stratégie de chunking.")
        else:
            insights.append(f"La variance des longueurs de chunks est faible (min: {stats['min_length']}, max: {stats['max_length']}), "
                           f"indiquant une segmentation cohérente du contenu médical.")
        
        # Insight 5: Quality assessment
        if stats['avg_length'] >= 50 and stats['avg_length'] <= 2000:
            insights.append(f"Les chunks respectent les critères de qualité RAG (longueur moyenne de {stats['avg_length']:.0f} caractères dans la plage acceptable [50-2000]), "
                           f"ce qui garantit une bonne qualité des futures embeddings.")
        else:
            insights.append(f"Certains chunks sont en dehors de la plage optimale [50-2000] caractères (moyenne: {stats['avg_length']:.0f}), "
                           f"ce qui pourrait nécessiter un post-traitement pour améliorer la qualité RAG.")
        
        return insights
    
    def create_visualization(self, stats: Dict[str, Any], save_path: str):
        """
        Create simple visualizations of EDA data
        
        Args:
            stats: Dictionary with EDA statistics
            save_path: Path to save visualization
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Chunk type distribution
        if stats['chunk_type_distribution']:
            types = list(stats['chunk_type_distribution'].keys())
            counts = list(stats['chunk_type_distribution'].values())
            
            axes[0].bar(types, counts)
            axes[0].set_title('Distribution des Types de Chunks Médicaux')
            axes[0].set_xlabel('Type Médical')
            axes[0].set_ylabel('Nombre de Chunks')
            axes[0].tick_params(axis='x', rotation=45)
        
        # Length statistics
        length_data = {
            'Moyenne': stats['avg_length'],
            'Min': stats['min_length'],
            'Max': stats['max_length'],
            'Médiane': stats['median_length']
        }
        
        axes[1].bar(length_data.keys(), length_data.values())
        axes[1].set_title('Statistiques de Longueur des Chunks')
        axes[1].set_ylabel('Caractères')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Visualization saved to {save_path}")
    
    def save_insights(self, insights: List[str], save_path: str):
        """
        Save insights to markdown file
        
        Args:
            insights: List of narrative insights
            save_path: Path to save insights
        """
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("# Insights Analyse Données RAG Médicales\n\n")
            f.write(f"Généré le {Path.cwd().name}\n\n")
            f.write("## Découvertes Clés\n\n")
            
            for i, insight in enumerate(insights, 1):
                f.write(f"{i}. {insight}\n\n")
        
        self.logger.info(f"Insights saved to {save_path}")

def main():
    """Main function to run EDA"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.processing.feature_engineering import MedicalFeatureEngineer
    from src.processing.chunker import MedicalTextChunker
    from src.ingestion.medical_loader import MedicalDocumentLoader
    from langchain_core.documents import Document
    
    # Initialize components
    loader = MedicalDocumentLoader()
    chunker = MedicalTextChunker()
    feature_engineer = MedicalFeatureEngineer()
    eda = MedicalRAGEDA()
    
    # Load and process
    documents = loader.load_sample_documents()
    chunks = chunker.chunk_documents(documents)
    
    # Extract features
    features = feature_engineer.extract_features(chunks)
    print(f"\n✅ Features extraites: {len(features)} chunks, {len(features[0])} features par chunk")
    print(f"📊 Résumé features: {feature_engineer.get_feature_summary(features)}")
    
    # Generate insights
    insights = feature_engineer.generate_insights(features)
    print(f"\n💡 Insights générés: {len(insights)}")
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")

if __name__ == "__main__":
    main()

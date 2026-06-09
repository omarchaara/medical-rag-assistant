"""
Medical Feature Engineering for RAG Pipeline
Creates additional features for medical text analysis
"""

import re
from typing import List, Dict, Any
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class MedicalFeatureEngineer:
    """Create features specific to medical text analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Medical terms for feature extraction
        self.medical_keywords = [
            'symptom', 'pain', 'fever', 'nausea', 'fatigue', 'headache',
            'treatment', 'therapy', 'medication', 'drug', 'surgery',
            'diagnosis', 'diagnostic', 'test', 'examination',
            'prevention', 'risk', 'factor', 'patient', 'clinical',
            'diabetes', 'cardiovascular', 'cardiac', 'hypertension'
        ]
        
    def extract_features(self, chunks: List[Document]) -> List[Dict[str, Any]]:
        """
        Extract features from chunks
        
        Args:
            chunks: List of chunked Document objects
            
        Returns:
            List of feature dictionaries
        """
        features_list = []
        
        for i, chunk in enumerate(chunks):
            text = chunk.page_content.lower()
            
            features = {
                "chunk_id": chunk.metadata.get('chunk_id', f'chunk_{i}'),
                # Basic text features
                "char_count": len(chunk.page_content),
                "word_count": len(chunk.page_content.split()),
                "sentence_count": text.count('.') + text.count('!') + text.count('?'),
                "paragraph_count": chunk.page_content.count('\n\n') + 1,
                
                # Medical domain features
                "medical_keyword_count": sum(1 for keyword in self.medical_keywords if keyword in text),
                "medical_keyword_density": sum(1 for keyword in self.medical_keywords if keyword in text) / max(len(chunk.page_content.split()), 1),
                
                # Text complexity features
                "avg_word_length": sum(len(word) for word in chunk.page_content.split()) / max(len(chunk.page_content.split()), 1),
                "unique_word_ratio": len(set(chunk.page_content.lower().split())) / max(len(chunk.page_content.split()), 1),
                
                # Punctuation features
                "question_count": text.count('?'),
                "exclamation_count": text.count('!'),
                "comma_count": text.count(','),
                
                # Number features
                "number_count": len(re.findall(r'\d+', chunk.page_content)),
                
                # Category features
                "chunk_type": chunk.metadata.get('chunk_type', 'unknown'),
                
                # Positional features
                "chunk_index": chunk.metadata.get('chunk_index', i),
                "total_chunks": chunk.metadata.get('total_chunks', len(chunks))
            }
            
            features_list.append(features)
        
        self.logger.info(f"Extracted {len(features_list)} feature sets from {len(chunks)} chunks")
        return features_list

    def generate_insights(self, features_list: List[Dict[str, Any]]) -> List[str]:
        """
        Generate narrative insights from features
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            List of narrative insight strings
        """
        insights = []
        
        if not features_list:
            return ["No chunks to analyze"]
        
        # Calculate aggregates
        avg_word_count = sum(f['word_count'] for f in features_list) / len(features_list)
        avg_medical_density = sum(f['medical_keyword_density'] for f in features_list) / len(features_list)
        chunk_types = [f['chunk_type'] for f in features_list]
        
        # Generate insights
        insights.append(f"Nous avons découvert que les chunks ont en moyenne {avg_word_count:.1f} mots, "
                       f"avec une densité de termes médicaux de {avg_medical_density:.3f} mots par token.")
        
        if chunk_types:
            type_counts = {}
            for t in chunk_types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            most_common = max(type_counts.items(), key=lambda x: x[1])
            insights.append(f"La catégorie médicale la plus fréquente est '{most_common[0]}' "
                           f"représentant {most_common[1]}/{len(chunk_types)} chunks ({most_common[1]/len(chunk_types)*100:.1f}%).")
        
        # Complexity insight
        avg_unique_ratio = sum(f['unique_word_ratio'] for f in features_list) / len(features_list)
        insights.append(f"Le vocabulaire médical montre un ratio de mots uniques de {avg_unique_ratio:.3f}, "
                       f"indiquant une {'diversité terminologique' if avg_unique_ratio > 0.7 else 'répétition terminologique'} significative.")
        
        return insights

    def get_feature_summary(self, features_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics of features
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            Dictionary with feature summary statistics
        """
        if not features_list:
            return {}
        
        summary = {
            "total_chunks": len(features_list),
            "avg_word_count": sum(f['word_count'] for f in features_list) / len(features_list),
            "avg_sentence_count": sum(f['sentence_count'] for f in features_list) / len(features_list),
            "avg_medical_keyword_count": sum(f['medical_keyword_count'] for f in features_list) / len(features_list),
            "total_medical_keywords": sum(f['medical_keyword_count'] for f in features_list),
            "chunk_types": list(set(f['chunk_type'] for f in features_list)),
            "avg_unique_word_ratio": sum(f['unique_word_ratio'] for f in features_list) / len(features_list)
        }
        
        return summary

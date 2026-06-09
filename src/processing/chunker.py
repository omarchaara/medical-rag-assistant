"""
Medical Text Chunker for RAG Pipeline
Chunks medical documents intelligently with medical boundary awareness
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)


class MedicalTextChunker:
    """Chunk medical documents with domain-aware splitting"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize medical text chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Recursive splitter that respects natural boundaries
        # Order: paragraphs, sentences, words, characters
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MedicalTextChunker initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into medical chunks with metadata preservation
        
        Args:
            documents: List of Document objects to chunk
            
        Returns:
            List of chunked Document objects with enhanced metadata
        """
        chunks = []
        
        for doc in documents:
            # Chunk the document
            doc_chunks = self.splitter.split_documents([doc])
            
            # Add chunk-specific metadata
            source = doc.metadata.get('source', 'unknown')
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_id": f"{source}_{i}",
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks),
                    "original_length": len(doc.page_content),
                    "chunk_length": len(chunk.page_content),
                    "chunk_type": self._classify_chunk_type(chunk.page_content)
                })
                chunks.append(chunk)
        
        self.logger.info(f"Chunking completed: {len(documents)} docs → {len(chunks)} chunks")
        return chunks

    def _classify_chunk_type(self, text: str) -> str:
        """
        Classify the type of medical chunk based on content
        
        Args:
            text: Chunk text content
            
        Returns:
            String indicating chunk type
        """
        text_lower = text.lower()
        
        # Medical keywords for classification
        classification_keywords = {
            'symptoms': ['symptom', 'pain', 'fever', 'nausea', 'fatigue', 'headache'],
            'treatment': ['treatment', 'therapy', 'medication', 'drug', 'surgery', 'management'],
            'diagnosis': ['diagnosis', 'diagnostic', 'test', 'examination', 'sign'],
            'prevention': ['prevention', 'preventive', 'vaccination', 'screening'],
            'prognosis': ['prognosis', 'outcome', 'survival', 'mortality'],
            'risk_factors': ['risk', 'factor', 'associated', 'predispose']
        }
        
        max_count = 0
        chunk_type = 'general'
        
        for category, keywords in classification_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > max_count:
                max_count = count
                chunk_type = category
        
        return chunk_type

    def analyze_chunks(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        Analyze chunk statistics and distributions
        
        Args:
            chunks: List of chunked Document objects
            
        Returns:
            Dictionary with chunk statistics
        """
        lengths = [len(chunk.page_content) for chunk in chunks]
        chunk_types = [chunk.metadata.get('chunk_type', 'unknown') for chunk in chunks]
        
        stats = {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) / len(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "median_length": sorted(lengths)[len(lengths) // 2] if lengths else 0,
            "chunk_type_distribution": {}
        }
        
        # Count chunk types
        for chunk_type in chunk_types:
            stats["chunk_type_distribution"][chunk_type] = stats["chunk_type_distribution"].get(chunk_type, 0) + 1
        
        self.logger.info(f"Chunk statistics: {stats}")
        return stats

    def filter_chunks_by_length(self, chunks: List[Document], min_length: int = 50, max_length: int = 2000) -> List[Document]:
        """
        Filter chunks by length to ensure quality
        
        Args:
            chunks: List of chunked Document objects
            min_length: Minimum chunk length
            max_length: Maximum chunk length
            
        Returns:
            Filtered list of Document objects
        """
        filtered = [
            chunk for chunk in chunks 
            if min_length <= len(chunk.page_content) <= max_length
        ]
        
        self.logger.info(f"Filtered chunks: {len(chunks)} → {len(filtered)} (length range: {min_length}-{max_length})")
        return filtered

    def merge_short_chunks(self, chunks: List[Document], threshold: int = 100) -> List[Document]:
        """
        Merge chunks that are too short with adjacent chunks
        
        Args:
            chunks: List of chunked Document objects
            threshold: Minimum length threshold for merging
            
        Returns:
            List of Document objects with short chunks merged
        """
        if not chunks:
            return chunks
            
        merged = []
        current_chunk = chunks[0]
        
        for chunk in chunks[1:]:
            if len(current_chunk.page_content) < threshold:
                # Merge with current chunk
                current_chunk.page_content += " " + chunk.page_content
                current_chunk.metadata["merged"] = True
                current_chunk.metadata["chunk_length"] = len(current_chunk.page_content)
            else:
                # Add current chunk and start new
                merged.append(current_chunk)
                current_chunk = chunk
        
        # Add the last chunk
        merged.append(current_chunk)
        
        self.logger.info(f"Merged short chunks: {len(chunks)} → {len(merged)}")
        return merged

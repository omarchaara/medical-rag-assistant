# src/processing/chunker.py


"""
Medical Text Chunker for RAG Pipeline
Intelligent chunking for medical documents with metadata enrichment
"""

import hashlib
import logging
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class MedicalTextChunker:
    """
    Medical document chunker optimized for RAG systems
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

        logger.info(
            f"MedicalTextChunker initialized "
            f"(size={chunk_size}, overlap={chunk_overlap})"
        )

    def chunk_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:

        chunks = []

        for doc in documents:

            source = doc.metadata.get(
                "source",
                "unknown"
            )

            doc_chunks = self.splitter.split_documents([doc])

            for index, chunk in enumerate(doc_chunks):

                chunk.metadata.update({
                    "chunk_id": f"{source}_{index}",
                    "chunk_index": index,
                    "total_chunks": len(doc_chunks),
                    "chunk_length": len(chunk.page_content),
                    "original_length": len(doc.page_content),
                    "chunk_hash": self.generate_chunk_hash(
                        chunk.page_content
                    ),
                    "chunk_type": self.classify_chunk_type(
                        chunk.page_content
                    ),
                    "medical_section": self.detect_medical_section(
                        chunk.page_content
                    ),
                    "quality_score": self.compute_quality_score(
                        chunk.page_content
                    ),
                    "source_document": source
                })

                if self.is_medical_content(
                    chunk.page_content
                ):
                    chunks.append(chunk)

        logger.info(
            f"Chunking completed : "
            f"{len(documents)} docs -> {len(chunks)} chunks"
        )

        return chunks

    def generate_chunk_hash(
        self,
        text: str
    ) -> str:

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def classify_chunk_type(
        self,
        text: str
    ) -> str:

        text_lower = text.lower()

        categories = {
            "symptoms": [
                "symptom",
                "pain",
                "fever",
                "fatigue",
                "headache",
                "nausea"
            ],
            "diagnosis": [
                "diagnosis",
                "diagnostic",
                "test",
                "examination"
            ],
            "treatment": [
                "treatment",
                "therapy",
                "medication",
                "drug",
                "management",
                "surgery"
            ],
            "prevention": [
                "prevention",
                "screening",
                "vaccination"
            ],
            "prognosis": [
                "prognosis",
                "survival",
                "outcome"
            ],
            "risk_factors": [
                "risk",
                "factor",
                "associated"
            ]
        }

        max_count = 0
        chunk_type = "general"

        for category, keywords in categories.items():

            count = sum(
                1
                for keyword in keywords
                if keyword in text_lower
            )

            if count > max_count:
                max_count = count
                chunk_type = category

        return chunk_type

    def detect_medical_section(
        self,
        text: str
    ) -> str:

        text_lower = text.lower()

        sections = {
            "introduction": [
                "introduction",
                "overview",
                "background"
            ],
            "symptoms": [
                "symptoms",
                "clinical presentation"
            ],
            "diagnosis": [
                "diagnosis",
                "diagnostic criteria"
            ],
            "treatment": [
                "treatment",
                "management",
                "therapy"
            ],
            "prevention": [
                "prevention",
                "prophylaxis"
            ],
            "references": [
                "references",
                "bibliography"
            ]
        }

        for section, keywords in sections.items():

            for keyword in keywords:

                if keyword in text_lower:
                    return section

        return "unknown"

    def compute_quality_score(
        self,
        text: str
    ) -> float:

        score = 1.0

        words = len(text.split())

        if words < 30:
            score -= 0.3

        if len(text) < 100:
            score -= 0.2

        if text.count(".") < 2:
            score -= 0.2

        return round(
            max(score, 0.0),
            2
        )

    def is_medical_content(
        self,
        text: str
    ) -> bool:

        medical_terms = [
            "patient",
            "treatment",
            "therapy",
            "disease",
            "diagnosis",
            "clinical",
            "medical",
            "symptom",
            "drug",
            "medication"
        ]

        score = sum(
            1
            for term in medical_terms
            if term in text.lower()
        )

        return score >= 1

    def filter_chunks_by_length(
        self,
        chunks: List[Document],
        min_length: int = 50,
        max_length: int = 2000
    ) -> List[Document]:

        filtered = [
            chunk
            for chunk in chunks
            if min_length <= len(chunk.page_content) <= max_length
        ]

        logger.info(
            f"Filtered chunks: "
            f"{len(chunks)} -> {len(filtered)}"
        )

        return filtered

    def merge_short_chunks(
        self,
        chunks: List[Document],
        threshold: int = 100
    ) -> List[Document]:

        if not chunks:
            return chunks

        merged = []

        current = chunks[0]

        for chunk in chunks[1:]:

            if len(current.page_content) < threshold:

                current.page_content += (
                    "\n" + chunk.page_content
                )

                current.metadata["merged"] = True

                current.metadata["chunk_length"] = len(
                    current.page_content
                )

            else:

                merged.append(current)

                current = chunk

        merged.append(current)

        logger.info(
            f"Merged chunks : "
            f"{len(chunks)} -> {len(merged)}"
        )

        return merged

    def analyze_chunks(
        self,
        chunks: List[Document]
    ) -> Dict[str, Any]:

        lengths = [
            len(chunk.page_content)
            for chunk in chunks
        ]

        stats = {
            "total_chunks": len(chunks),
            "avg_length": (
                sum(lengths) / len(lengths)
                if lengths else 0
            ),
            "min_length": (
                min(lengths)
                if lengths else 0
            ),
            "max_length": (
                max(lengths)
                if lengths else 0
            ),
            "chunk_type_distribution": {}
        }

        for chunk in chunks:

            chunk_type = chunk.metadata.get(
                "chunk_type",
                "unknown"
            )

            stats["chunk_type_distribution"][
                chunk_type
            ] = (
                stats["chunk_type_distribution"]
                .get(chunk_type, 0) + 1
            )

        logger.info(stats)

        return stats

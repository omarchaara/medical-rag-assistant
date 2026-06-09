"""
Medical Document Loader for RAG Pipeline
Loads PDF, HTML, and text medical documents
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pathlib import Path
import logging
from typing import List
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class MedicalDocumentLoader:
    """Loader for medical documents (PDF, HTML, text)"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        """
        Initialize medical document loader
        
        Args:
            data_dir: Directory containing medical documents
        """
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MedicalDocumentLoader initialized with data_dir: {data_dir}")
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a medical PDF document
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of Document objects (one per page)
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            self.logger.info(f"PDF loaded: {pdf_path} - {len(documents)} pages")
            return documents
        except Exception as e:
            self.logger.error(f"Error loading PDF {pdf_path}: {e}")
            raise

    def load_text(self, text_path: str) -> List[Document]:
        """
        Load a text document (guidelines, HTML converted to text)
        
        Args:
            text_path: Path to text file
            
        Returns:
            List of Document objects
        """
        try:
            loader = TextLoader(text_path, encoding='utf-8')
            documents = loader.load()
            self.logger.info(f"Text loaded: {text_path}")
            return documents
        except Exception as e:
            self.logger.error(f"Error loading text {text_path}: {e}")
            raise

    def load_directory(self) -> List[Document]:
        """
        Load all documents from the data directory
        
        Returns:
            List of all Document objects
        """
        all_documents = []
        
        # Load PDFs
        pdf_files = list(self.data_dir.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        for pdf_file in pdf_files:
            try:
                docs = self.load_pdf(str(pdf_file))
                all_documents.extend(docs)
            except Exception as e:
                self.logger.warning(f"Failed to load {pdf_file}: {e}")
        
        # Load text files
        text_files = list(self.data_dir.glob("*.txt"))
        self.logger.info(f"Found {len(text_files)} text files")
        for text_file in text_files:
            try:
                docs = self.load_text(str(text_file))
                all_documents.extend(docs)
            except Exception as e:
                self.logger.warning(f"Failed to load {text_file}: {e}")
        
        self.logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents

    def load_sample_documents(self) -> List[Document]:
        """
        Load sample medical documents for testing
        Creates sample data if no documents exist
        
        Returns:
            List of Document objects
        """
        # If directory is empty, create sample data
        if not any(self.data_dir.iterdir()):
            self.logger.warning("No documents found, creating sample data")
            self._create_sample_data()
            return self.load_directory()
        
        return self.load_directory()

    def _create_sample_data(self):
        """Create sample medical documents for testing"""
        sample_texts = [
            {
                "filename": "sample_cardiology.txt",
                "content": """
Cardiovascular Disease Guidelines
Symptoms of myocardial infarction include chest pain, shortness of breath, and nausea.
Risk factors include hypertension, diabetes, smoking, and family history.
Treatment options include antiplatelet therapy, beta-blockers, and statins.
"""
            },
            {
                "filename": "sample_diabetes.txt", 
                "content": """
Diabetes Management Guidelines
Type 2 diabetes is characterized by insulin resistance and relative insulin deficiency.
Symptoms include increased thirst, frequent urination, and unexplained weight loss.
Management includes lifestyle modifications, metformin, and cardiovascular risk reduction.
"""
            }
        ]
        
        for sample in sample_texts:
            file_path = self.data_dir / sample["filename"]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sample["content"])
            self.logger.info(f"Created sample file: {file_path}")

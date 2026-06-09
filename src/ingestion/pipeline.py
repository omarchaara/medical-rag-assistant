from src.ingestion.loader import MedicalDocumentLoader
from src.ingestion.extractor import PDFExtractor
from src.ingestion.validator import MedicalValidator
from src.ingestion.cleaner import MedicalCleaner

from src.processing.metadata import MetadataBuilder
from src.processing.chunker import TextChunker

loader = MedicalDocumentLoader()
extractor = PDFExtractor()
validator = MedicalValidator()
cleaner = MedicalCleaner()

metadata_builder = MetadataBuilder()
chunker = TextChunker()

docs = loader.list_documents()

records = []

for doc in docs:

    text = extractor.extract_text(doc)

    validator.validate(text)

    text = cleaner.clean(text)

    chunks = chunker.chunk(text)

    metadata = metadata_builder.build(
        doc.name,
        text
    )

    metadata["chunks"] = len(chunks)

    records.append(metadata)

print(records)
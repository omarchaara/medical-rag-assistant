from src.ingestion.loader import MedicalDocumentLoader
from src.ingestion.extractor import PDFExtractor
from src.ingestion.validator import MedicalValidator
from src.ingestion.cleaner import MedicalCleaner

from src.processing.metadata import MetadataBuilder
from src.processing.chunker import MedicalTextChunker
from langchain_core.documents import Document

loader = MedicalDocumentLoader()
extractor = PDFExtractor()
validator = MedicalValidator()
cleaner = MedicalCleaner()

metadata_builder = MetadataBuilder()
chunker = MedicalTextChunker()

docs = loader.list_documents()

print(f"Documents trouvés : {len(docs)}")

for d in docs:
    print("->", d)

records = []

for doc in docs:

    print(f"\nTraitement : {doc}")

    text = extractor.extract_text(doc)

    print("\nAperçu :")
    print(text[:300])

    validator.validate(text)

    text = cleaner.clean(text)

    document = Document(
        page_content=text,
        metadata={
            "source": doc.name
        }
    )

    chunks = chunker.chunk_documents([document])

    print(f"\nChunks générés : {len(chunks)}")

    if len(chunks) > 0:
        print("\nPremier chunk :")
        print(chunks[0].page_content[:200])

    metadata = metadata_builder.build(
        doc.name,
        text
    )

    metadata["chunks"] = len(chunks)

    records.append(metadata)

print("\nRésultat final :")
print(records)
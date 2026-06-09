from pathlib import Path

class MedicalDocumentLoader:

    def __init__(self, data_path="data/raw"):
        self.data_path = Path(data_path)

    def list_documents(self):

        return list(self.data_path.glob("*.pdf"))
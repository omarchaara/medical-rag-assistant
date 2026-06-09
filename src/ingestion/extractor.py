import fitz

class PDFExtractor:

    def extract_text(self, pdf_path):

        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        return text
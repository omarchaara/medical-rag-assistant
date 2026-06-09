from datetime import datetime

class MetadataBuilder:

    def build(self, filename, text):

        return {
            "document": filename,
            "length": len(text),
            "words": len(text.split()),
            "created_at": datetime.now().isoformat()
        }
class MedicalValidator:

    def validate(self, text):

        if len(text) < 100:

            raise ValueError(
                "Document trop petit"
            )

        return True
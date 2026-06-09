class DataQuality:

    def test_documents(self, df):

        assert len(df) > 0

        assert "document" in df.columns

        assert "words" in df.columns

        assert df["words"].min() > 50

        return True
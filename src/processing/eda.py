
"""
EDA Module for Medical RAG Project
Day 2 - Data Exploration & Quality Analysis
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class MedicalEDA:

    def __init__(self):

        self.logger = logging.getLogger(__name__)

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute complete EDA pipeline
        """

        self.logger.info("Starting EDA")

        stats = self.basic_statistics(df)

        self.document_statistics(df)

        self.missing_values_analysis(df)

        self.column_analysis(df)

        return stats

    def basic_statistics(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:

        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_usage_mb":
                round(
                    df.memory_usage(
                        deep=True
                    ).sum() / 1024 / 1024,
                    2
                )
        }

        print("\n=== DATASET OVERVIEW ===")
        print(f"Rows: {stats['rows']}")
        print(f"Columns: {stats['columns']}")
        print(f"Memory: {stats['memory_usage_mb']} MB")

        print("\n=== DESCRIBE ===")
        print(df.describe(include="all"))

        return stats

    def document_statistics(
        self,
        df: pd.DataFrame
    ):

        print("\n=== DOCUMENT STATISTICS ===")

        if "words" in df.columns:

            print(
                f"Average words: "
                f"{df['words'].mean():.2f}"
            )

            print(
                f"Min words: "
                f"{df['words'].min()}"
            )

            print(
                f"Max words: "
                f"{df['words'].max()}"
            )

        if "text_length" in df.columns:

            print(
                f"Average length: "
                f"{df['text_length'].mean():.2f}"
            )

    def missing_values_analysis(
        self,
        df: pd.DataFrame
    ):

        print("\n=== MISSING VALUES ===")

        missing = df.isnull().sum()

        print(missing)

        total_missing = missing.sum()

        print(
            f"\nTotal Missing Values: "
            f"{total_missing}"
        )

    def column_analysis(
        self,
        df: pd.DataFrame
    ):

        print("\n=== COLUMN TYPES ===")

        print(df.dtypes)

    def correlation_analysis(
        self,
        df: pd.DataFrame
    ):

        numeric_cols = df.select_dtypes(
            include=["number"]
        )

        if len(numeric_cols.columns) < 2:
            return

        print("\n=== CORRELATION MATRIX ===")

        print(
            numeric_cols.corr()
        )

    def quality_report(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:

        report = {
            "rows": len(df),
            "duplicates":
                df.duplicated().sum(),
            "missing_values":
                int(
                    df.isnull()
                    .sum()
                    .sum()
                )
        }

        if "words" in df.columns:

            report["avg_words"] = round(
                df["words"].mean(),
                2
            )

        return report

    def generate_insights(
        self,
        df: pd.DataFrame
    ) -> List[str]:

        insights = []

        insights.append(
            f"Dataset contains {len(df)} records."
        )

        if "words" in df.columns:

            avg_words = (
                df["words"].mean()
            )

            insights.append(
                f"Average document size is "
                f"{avg_words:.0f} words."
            )

        duplicates = (
            df.duplicated().sum()
        )

        insights.append(
            f"{duplicates} duplicate rows detected."
        )

        return insights

    def create_visualizations(
        self,
        df: pd.DataFrame,
        output_dir="reports"
    ):

        output_path = Path(output_dir)

        output_path.mkdir(
            parents=True,
            exist_ok=True
        )

        if "words" in df.columns:

            plt.figure(
                figsize=(8, 5)
            )

            plt.hist(
                df["words"],
                bins=20
            )

            plt.title(
                "Words Distribution"
            )

            plt.xlabel(
                "Number of Words"
            )

            plt.ylabel(
                "Frequency"
            )

            plt.tight_layout()

            plt.savefig(
                output_path /
                "words_distribution.png"
            )

            plt.close()

            self.logger.info(
                "Visualization saved"
            )
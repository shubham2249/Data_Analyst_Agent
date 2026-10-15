import pandas as pd
import pytest

from app.tools.ingestion import (
    DatasetIngestion,
    DatasetIngestionError,
)


def test_load_csv():

    content = b"name,age\nAlice,20\nBob,25\n"

    ingestion = DatasetIngestion()

    df = ingestion.load(
        filename="users.csv",
        content=content,
    )

    assert isinstance(df, pd.DataFrame)

    assert len(df) == 2
    assert list(df.columns) == ["name", "age"]


def test_reject_unsupported_file():

    ingestion = DatasetIngestion()

    with pytest.raises(DatasetIngestionError):

        ingestion.load(
            filename="data.exe",
            content=b"some content",
        )


def test_reject_empty_file():

    ingestion = DatasetIngestion()

    with pytest.raises(DatasetIngestionError):

        ingestion.load(
            filename="data.csv",
            content=b"",
        )
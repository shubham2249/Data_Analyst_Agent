from io import BytesIO

import pandas as pd

from app.core.config import settings


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".json",
}


class DatasetIngestionError(Exception):
    pass


class DatasetIngestion:

    def load(self, filename: str, content: bytes) -> pd.DataFrame:

        self._validate_file_size(content)

        extension = self._get_extension(filename)

        if extension not in SUPPORTED_EXTENSIONS:
            raise DatasetIngestionError(
                f"Unsupported file type: {extension}"
            )

        if not content:
            raise DatasetIngestionError(
                "Uploaded file is empty."
            )

        try:

            if extension == ".csv":
                return pd.read_csv(BytesIO(content))

            if extension == ".xlsx":
                return pd.read_excel(BytesIO(content))

            if extension == ".json":
                return pd.read_json(BytesIO(content))

        except Exception as exc:

            raise DatasetIngestionError(
                f"Failed to read dataset: {exc}"
            ) from exc

        raise DatasetIngestionError(
            "Unable to determine how to load the dataset."
        )

    @staticmethod
    def _get_extension(filename: str) -> str:

        filename = filename.lower().strip()

        if "." not in filename:
            return ""

        return "." + filename.rsplit(".", 1)[1]

    @staticmethod
    def _validate_file_size(content: bytes):

        max_size = settings.max_file_size_mb * 1024 * 1024

        if len(content) > max_size:
            raise DatasetIngestionError(
                f"File exceeds maximum size of "
                f"{settings.max_file_size_mb} MB."
            )
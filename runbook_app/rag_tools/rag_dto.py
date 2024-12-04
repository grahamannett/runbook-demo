from dataclasses import dataclass
from enum import StrEnum, auto

from rxconstants import rag_docs_storage_type


class StorageType(StrEnum):
    TABLE = auto()
    FILE = auto()


storage_type: StorageType = StorageType(rag_docs_storage_type)


@dataclass
class DocumentDTO:
    """Data Transfer Object for document storage and retrieval.

    This class represents a document in a format ready for storage/retrieval
    in either a database or file system.

    Attributes:
        text: The main content of the document
        title: The document's title
        url: Source URL of the document
    """

    text: str
    title: str
    url: str

    def __getitem__(self, key: str) -> str:
        """Enable dict-like access to attributes.

        Args:
            key: The attribute name to access

        Returns:
            The value of the requested attribute
        """
        return getattr(self, key)

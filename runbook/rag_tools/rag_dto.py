from enum import StrEnum, auto

from rxconstants import rag_docs_storage_type


class StorageType(StrEnum):
    TABLE = auto()
    FILE = auto()


storage_type: StorageType = StorageType(rag_docs_storage_type)

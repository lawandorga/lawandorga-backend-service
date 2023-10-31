from .note import router as note_router
from .org import router as org_router
from .query import router as query_router

__all__ = [
    "note_router",
    "org_router",
    "query_router",
]

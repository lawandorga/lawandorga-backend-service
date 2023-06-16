from .error_statistics import router as error_statistics_router
from .general_statistics import router as general_statistics_router
from .individual_statistics import router as individual_statistics_router
from .org_statistics import router as rlc_statistics_router
from .record_statistics import router as record_statistics_router

__all__ = [
    "error_statistics_router",
    "general_statistics_router",
    "individual_statistics_router",
    "rlc_statistics_router",
    "record_statistics_router",
]

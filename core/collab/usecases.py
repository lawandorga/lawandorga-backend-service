from core.collab.use_cases.collab import (
    create_collab,
    delete_collab,
    optimize,
    sync_collab,
    update_collab,
)

USECASES = {
    "collab/create_collab": create_collab,
    "collab/update_collab": update_collab,
    "collab/sync_collab": sync_collab,
    "collab/delete_collab": delete_collab,
    "collab/optimize": optimize,
}

from core.collab.use_cases.collab import (
    create_collab,
    delete_collab,
    optimize,
    sync_collab,
    update_collab,
)
from core.seedwork.use_case_layer import use_case


@use_case
def placeholder(__actor: None):
    pass


USECASES = {
    "collab/create_collab": create_collab,
    "collab/update_collab": update_collab,
    "collab/sync_collab": sync_collab,
    "collab/delete_collab": delete_collab,
    "collab/optimize": optimize,
    "collab/create_letterhead": placeholder,
    "collab/update_letterhead": placeholder,
    "collab/delete_letterhead": placeholder,
    "collab/create_footer": placeholder,
    "collab/update_footer": placeholder,
    "collab/delete_footer": placeholder,
}

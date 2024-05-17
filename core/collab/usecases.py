from core.collab.use_cases.collab import (
    create_collab,
    delete_collab,
    optimize,
    sync_collab,
    update_collab,
)
from core.collab.use_cases.letterhead import (
    create_letterhead,
    delete_letterhead,
    update_letterhead,
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
    "collab/create_letterhead": create_letterhead,
    "collab/update_letterhead": update_letterhead,
    "collab/delete_letterhead": delete_letterhead,
    "collab/create_footer": placeholder,
    "collab/update_footer": placeholder,
    "collab/delete_footer": placeholder,
}

from core.collab.use_cases.collab import (
    assign_template_to_collab,
    create_collab,
    delete_collab,
    optimize,
    sync_collab,
    update_collab_title,
)
from core.collab.use_cases.footer import create_footer, delete_footer, update_footer
from core.collab.use_cases.letterhead import (
    create_letterhead,
    delete_letterhead,
    update_letterhead,
)
from core.collab.use_cases.template import (
    create_template,
    delete_template,
    update_template,
)
from core.seedwork.use_case_layer import use_case


@use_case
def placeholder(__actor: None):
    pass


USECASES = {
    "collab/create_collab": create_collab,
    "collab/update_collab_title": update_collab_title,
    "collab/sync_collab": sync_collab,
    "collab/delete_collab": delete_collab,
    "collab/optimize": optimize,
    "collab/create_letterhead": create_letterhead,
    "collab/update_letterhead": update_letterhead,
    "collab/delete_letterhead": delete_letterhead,
    "collab/create_footer": create_footer,
    "collab/update_footer": update_footer,
    "collab/delete_footer": delete_footer,
    "collab/assign_template_to_collab": assign_template_to_collab,
    "collab/create_template": create_template,
    "collab/update_template": update_template,
    "collab/delete_template": delete_template,
}

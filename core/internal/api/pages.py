from core.internal.models import HelpPage, ImprintPage, IndexPage, TomsPage
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get("help/", output_schema=schemas.OutputHelpPage)
def query__help_page():
    page = HelpPage.get_solo()
    return {"id": page.id, "manual": page.manual.url if page.manual else ""}


@router.get("index/", output_schema=schemas.OutputIndexPage)
def query__index_page():
    return IndexPage.get_solo()


@router.get("imprint/", output_schema=schemas.OutputImprintPage)
def query__imprint_page():
    return ImprintPage.get_solo()


@router.get("toms/", output_schema=schemas.OutputTomsPage)
def query__toms_page():
    return TomsPage.get_solo()

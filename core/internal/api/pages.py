from typing import Optional

from django.shortcuts import get_object_or_404

from core.auth.models import OrgUser
from core.internal.models import (
    Article,
    HelpPage,
    ImprintPage,
    IndexPage,
    RoadmapItem,
    TomsPage,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get("article/<int:id>/", output_schema=schemas.OutputArticleDetail)
def query__article_page(data: schemas.InputArticleDetail, org_user: Optional[OrgUser]):
    # public endpoint: anonymous visitors only get articles for everyone,
    # members additionally get the articles addressed to their org
    org = org_user.org if org_user is not None else None
    return get_object_or_404(Article.objects.visible_to(org), pk=data.id)


@router.get("help/", output_schema=schemas.OutputHelpPage)
def query__help_page():
    page = HelpPage.get_solo()
    return page


@router.get("index/", output_schema=schemas.OutputIndexPage)
def query__index_page():
    page = IndexPage.get_solo()
    roadmap_items = list(RoadmapItem.objects.all())
    articles = list(Article.objects.public())
    return {
        "content": page.content,
        "roadmap_items": roadmap_items,
        "articles": articles,
    }


@router.get("imprint/", output_schema=schemas.OutputImprintPage)
def query__imprint_page():
    return ImprintPage.get_solo()


@router.get("toms/", output_schema=schemas.OutputTomsPage)
def query__toms_page():
    return TomsPage.get_solo()

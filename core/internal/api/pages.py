from django.shortcuts import get_object_or_404

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
def query__article_page(data: schemas.InputArticleDetail):
    return get_object_or_404(Article, pk=data.id)


@router.get("help/", output_schema=schemas.OutputHelpPage)
def query__help_page():
    page = HelpPage.get_solo()
    return page


@router.get("index/", output_schema=schemas.OutputIndexPage)
def query__index_page():
    page = IndexPage.get_solo()
    roadmap_items = list(RoadmapItem.objects.all())
    articles = list(Article.objects.all())
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

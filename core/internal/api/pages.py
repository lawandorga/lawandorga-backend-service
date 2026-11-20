from typing import Optional

from django.shortcuts import get_object_or_404

from core.auth.models import OrgUser
from core.internal.models import (
    Article,
    FeatureArea,
    HelpPage,
    ImprintPage,
    IndexPage,
    RoadmapItem,
    TomsPage,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()

# number of public articles on the landing page and in the public list
INDEX_PAGE_ARTICLES = 3
PUBLIC_ARTICLE_LIST_LIMIT = 50


@router.get("article/<int:id>/", output_schema=schemas.OutputArticleDetail)
def query__article_page(data: schemas.InputArticleDetail, org_user: Optional[OrgUser]):
    # public endpoint: anonymous visitors only get articles for everyone,
    # members additionally get the articles addressed to their org
    org = org_user.org if org_user is not None else None
    return get_object_or_404(Article.objects.visible_to(org), pk=data.id)


@router.get("articles/", output_schema=list[schemas.OutputArticleList])
def query__public_articles():
    # public list for "Alle Neuigkeiten": only articles for everyone
    return list(Article.objects.public().order_by("-date")[:PUBLIC_ARTICLE_LIST_LIMIT])


@router.get("help/", output_schema=schemas.OutputHelpPage)
def query__help_page():
    page = HelpPage.get_solo()
    return page


@router.get("index/", output_schema=schemas.OutputIndexPage)
def query__index_page():
    page = IndexPage.get_solo()
    roadmap_items = list(RoadmapItem.objects.filter(is_published=True))
    feature_areas = list(FeatureArea.objects.filter(is_published=True))
    articles = list(Article.objects.public().order_by("-date")[:INDEX_PAGE_ARTICLES])
    return {
        "content": page.content,
        "roadmap_items": roadmap_items,
        "feature_areas": feature_areas,
        "articles": articles,
    }


@router.get("imprint/", output_schema=schemas.OutputImprintPage)
def query__imprint_page():
    return ImprintPage.get_solo()


@router.get("toms/", output_schema=schemas.OutputTomsPage)
def query__toms_page():
    return TomsPage.get_solo()

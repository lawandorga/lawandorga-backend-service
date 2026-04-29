from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from core.auth.models import OrgUser
from core.internal.api.schemas import OutputArticleList
from core.internal.models import Article
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get("", output_schema=list[schemas.OutputArticleList])
def query_articles(org_user: OrgUser) -> list[OutputArticleList]:
    articles = Article.objects.filter(recipients=org_user.org).distinct()

    return [OutputArticleList.model_validate(article) for article in articles]


@router.get("dashboard/", output_schema=list[OutputArticleList])
def latest_articles(org_user: OrgUser) -> list[OutputArticleList]:
    cutoff_date = timezone.now() - timedelta(days=60)
    articles = Article.objects.filter(
        Q(date__gte=cutoff_date)
        & (Q(recipients__isnull=True) | Q(recipients=org_user.org))
    ).distinct()

    return [OutputArticleList.model_validate(article) for article in articles]

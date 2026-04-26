from datetime import timedelta

from django.db.models import Q, QuerySet
from django.utils import timezone

from core.auth.models import OrgUser
from core.internal.api.schemas import OutputArticleList
from core.internal.models import Article
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


def add_orgs_to_articles(articles: QuerySet[Article]) -> list[OutputArticleList]:
    return [
        OutputArticleList(
            id=article.pk,
            title=article.title,
            preview=article.preview,
            date=article.date,
        )
        for article in articles
    ]


@router.get("", output_schema=list[schemas.OutputArticleList])
def query_articles() -> list[OutputArticleList]:
    articles = Article.objects.all()

    if not articles:
        return []

    return add_orgs_to_articles(articles)


@router.get("dashboard/", output_schema=list[OutputArticleList])
def latest_articles(org_user: OrgUser) -> list[OutputArticleList]:
    cutoff_date = timezone.now() - timedelta(days=60)
    articles = (
        Article.objects.filter(
            Q(date__gte=cutoff_date)
            & (Q(recipients__isnull=True) | Q(recipients=org_user.org))
        )
        .distinct()
    )

    if not articles:
        return []

    return add_orgs_to_articles(articles)

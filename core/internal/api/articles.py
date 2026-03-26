from datetime import timedelta

from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from core.auth.api.org_user import OutputOrgUser
from core.auth.models import OrgUser
from core.internal.api.schemas import OutputArticleList
from core.internal.models import Article
from core.org.models import Org
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


def _users_of_orgs(orgs: list[Org]) -> list[OutputOrgUser]:
    seen: set[int] = set()
    result = []
    for org in orgs:
        for user in org.users.all():
            if user.pk not in seen:
                seen.add(user.pk)
                result.append(OutputOrgUser.model_validate(user))
    return result


def add_orgs_to_articles(articles: QuerySet[Article]) -> list[OutputArticleList]:
    result: list[OutputArticleList] = []
    all_orgs = list(Org.objects.prefetch_related("users"))

    for article in articles:
        recipient_orgs = getattr(article, "prefetched_recipients", [])

        if not recipient_orgs:
            recipient_orgs = all_orgs

        recipients = _users_of_orgs(recipient_orgs)

        result.append(
            OutputArticleList(
                id=article.pk,
                title=article.title,
                preview=article.preview,
                recipients=recipients,
                date=article.date,
            )
        )

    return result


@router.get("", output_schema=list[schemas.OutputArticleList])
def query_articles() -> list[OutputArticleList]:
    articles = Article.objects.prefetch_related(
        Prefetch(
            "recipients",
            queryset=Org.objects.prefetch_related("users"),
            to_attr="prefetched_recipients",
        )
    ).all()

    if not articles:
        return []

    return add_orgs_to_articles(articles)


@router.get("dashboard/", output_schema=list[OutputArticleList])
def latest_articles(org_user: OrgUser) -> list[OutputArticleList]:
    cutoff_date = timezone.now() - timedelta(days=60)
    articles = (
        Article.objects.prefetch_related(
            Prefetch(
                "recipients",
                queryset=Org.objects.prefetch_related("users"),
                to_attr="prefetched_recipients",
            )
        )
        .filter(
            Q(date__gte=cutoff_date)
            & (Q(recipients__isnull=True) | Q(recipients=org_user.org))
        )
        .distinct()
    )

    if not articles:
        return []

    return add_orgs_to_articles(articles)

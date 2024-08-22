from datetime import timedelta

from django.utils import timezone

from core.internal.api.schemas import OutputArticleList
from core.internal.models import Article
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get("", output_schema=list[schemas.OutputArticleList])
def query__articles():
    return list(Article.objects.all())


@router.get("dashboard/", output_schema=list[OutputArticleList])
def latest_articles():
    cutoff_date = timezone.now() - timedelta(days=60)
    articles = list(Article.objects.filter(date__gte=cutoff_date))
    return articles

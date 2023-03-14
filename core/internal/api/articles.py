from core.internal.models import Article
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get("", output_schema=list[schemas.OutputArticleList])
def query__articles():
    return list(Article.objects.all())

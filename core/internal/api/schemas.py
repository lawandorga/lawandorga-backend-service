from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OutputRoadmapItem(BaseModel):
    title: str
    description: str
    date: date
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputImprintPage(BaseModel):
    id: int
    content: str = ""

    model_config = ConfigDict(from_attributes=True)


class OutputHelpPage(BaseModel):
    id: int
    manual_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class OutputArticleList(BaseModel):
    id: int
    title: str
    description: str
    date: date

    model_config = ConfigDict(from_attributes=True)


class InputArticleDetail(BaseModel):
    id: int


class OutputArticleDetail(BaseModel):
    id: int
    title: str
    description: str
    date: date
    content: str = ""
    author_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutputIndexPage(BaseModel):
    content: str
    roadmap_items: list[OutputRoadmapItem]
    articles: list[OutputArticleList]

    model_config = ConfigDict(from_attributes=True)


class OutputTomsPage(BaseModel):
    id: int
    content: str = ""

    model_config = ConfigDict(from_attributes=True)

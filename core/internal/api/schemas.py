from datetime import date
from typing import Optional

from pydantic import BaseModel


class OutputRoadmapItem(BaseModel):
    title: str
    description: str
    date: date
    id: int

    class Config:
        orm_mode = True


class OutputImprintPage(BaseModel):
    id: int
    content: str = ""

    class Config:
        orm_mode = True


class OutputHelpPage(BaseModel):
    id: int
    manual_url: Optional[str]

    class Config:
        orm_mode = True


class OutputArticleList(BaseModel):
    id: int
    title: str
    description: str
    date: date

    class Config:
        orm_mode = True


class InputArticleDetail(BaseModel):
    id: int


class OutputArticleDetail(BaseModel):
    id: int
    title: str
    description: str
    date: date
    content: str = ""
    author_name: Optional[str] = None

    class Config:
        orm_mode = True


class OutputIndexPage(BaseModel):
    content: str
    roadmap_items: list[OutputRoadmapItem]
    articles: list[OutputArticleList]

    class Config:
        orm_mode = True


class OutputTomsPage(BaseModel):
    id: int
    content: str = ""

    class Config:
        orm_mode = True

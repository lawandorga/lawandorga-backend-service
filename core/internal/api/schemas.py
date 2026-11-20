from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class OutputRoadmapItem(BaseModel):
    title: str
    description: str
    date: date
    id: int
    status: Literal["live", "planned"]
    stage: str
    # the model stores one benefit per line, the api returns a list
    benefits: list[str] = Field(validation_alias="benefit_list")
    status_note: str
    icon_url: Optional[str]
    position: int

    model_config = ConfigDict(from_attributes=True)


class OutputFeatureArea(BaseModel):
    id: int
    title: str
    description: str
    placement: Literal["showroom", "more"]
    position: int
    icon_url: Optional[str]
    screenshot_url: Optional[str]
    screenshot_alt: str
    screenshot_note: str

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
    preview: str
    date: date

    model_config = ConfigDict(from_attributes=True)


class InputArticleDetail(BaseModel):
    id: int


class OutputArticleDetail(BaseModel):
    id: int
    title: str
    preview: str
    date: date
    content: str = ""
    author_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutputIndexPage(BaseModel):
    content: str
    roadmap_items: list[OutputRoadmapItem]
    feature_areas: list[OutputFeatureArea]
    articles: list[OutputArticleList]

    model_config = ConfigDict(from_attributes=True)


class OutputTomsPage(BaseModel):
    id: int
    content: str = ""

    model_config = ConfigDict(from_attributes=True)

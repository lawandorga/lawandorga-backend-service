from datetime import date

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
    manual: str

    class Config:
        orm_mode = True


class OutputIndexPage(BaseModel):
    content: str
    roadmap_items: list[OutputRoadmapItem]

    class Config:
        orm_mode = True


class OutputTomsPage(BaseModel):
    id: int
    content: str = ""

    class Config:
        orm_mode = True

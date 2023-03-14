from pydantic import BaseModel


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
    id: int
    content: str

    class Config:
        orm_mode = True


class OutputTomsPage(BaseModel):
    id: int
    content: str = ""

    class Config:
        orm_mode = True

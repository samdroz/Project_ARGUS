from pydantic import BaseModel


class TextRequest(BaseModel):
    title: str
    content: str
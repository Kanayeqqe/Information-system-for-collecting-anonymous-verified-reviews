from typing import List
from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    text: str

class ReplyOut(BaseModel):
    id: int
    text: str
    created_at: str

    class Config:
        orm_mode = True

class FeedbackOut(BaseModel):
    id: int
    text: str
    status: str
    moderation_notes: str | None = None
    created_at: str
    replies: List[ReplyOut] = []

    class Config:
        orm_mode = True
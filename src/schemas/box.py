from typing import List
from pydantic import BaseModel

class BoxCreateResponse(BaseModel):
    uuid: str
    owner_token: str

    class Config:
        orm_mode = True

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

class BoxFeedbacksResponse(BaseModel):
    uuid: str
    feedbacks: List[FeedbackOut] = []

    class Config:
        orm_mode = True
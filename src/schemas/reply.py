from pydantic import BaseModel

class ReplyCreate(BaseModel):
    text: str

class ReplyOut(BaseModel):
    id: int
    text: str
    created_at: str

    class Config:
        orm_mode = True
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CommentCreate(BaseModel):
    author: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)

class Comment(CommentCreate):
    id: int
    post_id: int
    created_at: datetime

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)

class Post(PostCreate):
    id: int
    created_at: datetime
    comments: Optional[list[Comment]] = []

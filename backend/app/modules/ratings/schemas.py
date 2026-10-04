from pydantic import BaseModel, Field

class RatingCreate(BaseModel):
    customer_id: str
    stars: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)

class RatingOut(RatingCreate):
    order_id: str
    created_at: str

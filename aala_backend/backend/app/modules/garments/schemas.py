from pydantic import BaseModel, Field
class GarmentCategoryOut(BaseModel):
    code: str
    name: str
    small_garment: bool = False
    active: bool = True
    display_order: int = 0
class GarmentCategoryCreate(BaseModel):
    code: str = Field(min_length=2,max_length=50)
    name: str = Field(min_length=2,max_length=150)
    small_garment: bool = False
    display_order: int = 0

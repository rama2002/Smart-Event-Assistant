from pydantic import BaseModel

class InterestBase(BaseModel):
    name: str

class InterestCreate(InterestBase):
    pass

class InterestUpdate(InterestBase):
    pass

class Interest(BaseModel):
    interest_id: int
    name: str

    class Config:
        orm_mode = True
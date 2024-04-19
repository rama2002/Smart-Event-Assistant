from pydantic import BaseModel

class UserInterest(BaseModel):
    id: int
    user_id: int
    interest_id: int

    class Config:
        orm_mode = True
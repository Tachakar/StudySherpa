from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    model_config = {"frozen": True}


class UserPublic(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True, "frozen": True}

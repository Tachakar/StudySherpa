from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    model_config = {"frozen": True}


class UserPublic(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True, "frozen": True}


class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = {"frozen": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = {"frozen": True}

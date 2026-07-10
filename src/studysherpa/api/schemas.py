from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    model_config = {"frozen": True}


class UserPublic(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True, "frozen": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

    model_config = {"frozen": True}


class RefreshRequest(BaseModel):
    refresh_token: str
    model_config = {"frozen": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = {"frozen": True}

from pydantic import BaseModel, ConfigDict, EmailStr

from .models import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    age: int | None
    phone: str | None
    bio: str | None
    avatar_url: str | None
    role: Role


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

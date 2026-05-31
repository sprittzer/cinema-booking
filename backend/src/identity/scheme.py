from pydantic import BaseModel, ConfigDict, EmailStr

from .models import Role


class CreateAdminUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Role = Role.USER


class UpdateUserAdminRequest(BaseModel):
    role: Role | None = None
    is_active: bool | None = None


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
    reviews_count: int = 0


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class UserReviewResponse(BaseModel):
    id: int
    movie_id: int
    movie_title: str
    score: int
    text: str | None
    likes: int = 0
    dislikes: int = 0

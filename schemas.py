from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=65)
    email: EmailStr = Field(max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=65)
    email: EmailStr | None = Field(default=None, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


class PostBase(BaseModel):
    title: str = Field(min_length=2, max_length=90)
    content: str = Field(min_length=5)


class PostCreate(PostBase):
    is_announcement: bool = False


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=90)
    content: str | None = Field(default=None, min_length=5)
    is_announcement: bool | None = None


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    likes: int
    comments_count: int
    is_announcement: bool
    author: UserPublic


class LikeResponse(BaseModel):
    post_id: int
    likes: int
    liked: bool


class LikedPostsResponse(BaseModel):
    post_ids: list[int]


class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentResponse(CommentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int
    date_posted: datetime
    author: UserPublic


class PaginatedCommentsResponse(BaseModel):
    comments: list[CommentResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

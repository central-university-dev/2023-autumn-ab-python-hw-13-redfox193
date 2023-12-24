from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    username: str
    is_admin: bool


class UserCreate(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    password: str


class User(BaseUser):
    id: int
    username: str
    is_admin: bool
    hashed_password: str


class BaseTodo(BaseModel):
    content: str


class TodoCreate(BaseTodo):
    content: str
    owner_username: str


class Todo(BaseModel):
    id: int
    content: str
    owner_id: int

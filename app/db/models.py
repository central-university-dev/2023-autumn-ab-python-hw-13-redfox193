from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    is_admin: bool



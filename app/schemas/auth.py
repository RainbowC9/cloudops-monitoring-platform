from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

class AccessResponse(BaseModel):
    message: str
    username: str
    role: str
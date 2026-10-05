from pydantic import BaseModel, EmailStr, Field


class RecoveryRequest(BaseModel):
    email: EmailStr


class RecoveryVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=12)


class RecoveryVerifyResponse(BaseModel):
    reset_token: str
    message: str


class RecoveryComplete(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=10, max_length=128)


class RecoveryMessage(BaseModel):
    message: str

from pydantic import BaseModel, EmailStr, Field


class RegistrationStartResponse(BaseModel):
    message: str
    email: EmailStr
    requires_verification: bool = True


class VerifyRegistrationRequest(BaseModel):
    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=12,
    )


class ResendRegistrationCodeRequest(BaseModel):
    email: EmailStr


class ChangeRegistrationEmailRequest(BaseModel):
    current_email: EmailStr
    new_email: EmailStr

    password: str = Field(
        min_length=10,
        max_length=128,
    )


class RegistrationEmailChangeResponse(BaseModel):
    message: str
    email: EmailStr


class LoginStartResponse(BaseModel):
    message: str
    email: EmailStr
    requires_mfa: bool = True


class VerifyLoginRequest(BaseModel):
    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=12,
    )


class MessageResponse(BaseModel):
    message: str
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from app.schemas.user import UserMe


class EditorialLoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=10,
        max_length=128,
    )


class EditorialLoginResponse(BaseModel):
    message: str

    requires_setup: bool

    requires_mfa: bool = True


class EditorialMfaSetupResponse(BaseModel):
    issuer: str

    account: EmailStr

    secret: str

    otpauth_uri: str


class EditorialMfaConfirmRequest(BaseModel):
    code: str = Field(
        min_length=6,
        max_length=6,
    )


class EditorialMfaVerifyRequest(BaseModel):
    code: str | None = Field(
        default=None,
        max_length=6,
    )

    recovery_code: str | None = Field(
        default=None,
        max_length=64,
    )


class EditorialMfaSetupSuccess(BaseModel):
    message: str

    recovery_codes: list[str]

    user: UserMe


class EditorialAuthSuccess(BaseModel):
    message: str

    user: UserMe
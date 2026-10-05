from fastapi import APIRouter

from app.api.routes import (
    account_recovery,
    admin,
    amplification,
    analytics,
    auth,
    contact,
    editorial,
    editorial_auth,
    messages,
    platform,
    publications,
    researchers,
    trust,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(account_recovery.router, prefix="/account-recovery", tags=["account-recovery"])
api_router.include_router(editorial_auth.router, prefix="/auth/editorial", tags=["editorial-auth"])
api_router.include_router(publications.router, prefix="/publications", tags=["publications"])
api_router.include_router(researchers.router, prefix="/researchers", tags=["researchers"])
api_router.include_router(editorial.router, prefix="/editorial", tags=["editorial"])
api_router.include_router(amplification.router, prefix="/amplification", tags=["research-amplification"])
api_router.include_router(trust.router, prefix="/trust", tags=["research-trust-vault"])
api_router.include_router(platform.router, tags=["platform-tools"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

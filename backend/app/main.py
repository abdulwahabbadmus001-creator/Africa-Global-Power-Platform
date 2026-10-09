from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from app.api.router import api_router
from app.core.config import settings

def _production_configuration_guard() -> None:
    if settings.environment != "production": return
    unsafe=[]
    if settings.secret_key == "change-me": unsafe.append("SECRET_KEY")
    if settings.mfa_secret_key == "change-this-mfa-secret": unsafe.append("MFA_SECRET_KEY")
    if settings.trust_log_secret == "change-this-trust-log-secret": unsafe.append("TRUST_LOG_SECRET")
    if not settings.cookie_secure: unsafe.append("COOKIE_SECURE")
    if "*" in settings.cors_origin_list: unsafe.append("CORS_ORIGINS")
    if not settings.public_site_url.lower().startswith("https://"): unsafe.append("PUBLIC_SITE_URL")
    if unsafe: raise RuntimeError("Unsafe production configuration: " + ", ".join(unsafe))

_production_configuration_guard()
app=FastAPI(title=settings.app_name,version="1.0.0",description="Africa & Global Power research publishing, trust, editorial, data and collaboration API.",docs_url="/docs" if settings.environment!="production" else None,redoc_url="/redoc" if settings.environment!="production" else None)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["GET","POST","PATCH","PUT","DELETE","OPTIONS"],allow_headers=["Content-Type","Authorization","X-Requested-With"])
UNSAFE_METHODS={"POST","PUT","PATCH","DELETE"}
def _allowed_browser_origins():
    values={o.strip().rstrip("/") for o in settings.cors_origin_list if o.strip()}
    if settings.public_site_url.strip(): values.add(settings.public_site_url.strip().rstrip("/"))
    return values

@app.middleware("http")
async def security_boundary(request:Request,call_next):
    blocked=None
    if settings.environment=="production" and request.method.upper() in UNSAFE_METHODS:
        origin=request.headers.get("origin")
        fetch_site=request.headers.get("sec-fetch-site","").lower()
        if origin and origin.rstrip("/") not in _allowed_browser_origins(): blocked=JSONResponse(status_code=403,content={"detail":"Cross-origin state-changing request blocked."})
        elif fetch_site=="cross-site": blocked=JSONResponse(status_code=403,content={"detail":"Cross-site state-changing request blocked."})
    response:Response=blocked or await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    response.headers["Cross-Origin-Opener-Policy"]="same-origin"
    response.headers["Content-Security-Policy"]="default-src 'none'; frame-ancestors 'none'; base-uri 'none'; style-src 'unsafe-inline'"
    if request.cookies.get("access_token") or request.url.path.startswith(f"{settings.api_v1_prefix}/auth"): response.headers["Cache-Control"]="no-store"
    if settings.environment=="production": response.headers["Strict-Transport-Security"]="max-age=31536000; includeSubDomains"
    return response

@app.get("/health")
def health(): return {"status":"ok","service":"agp-api","version":"1.0.0"}
app.include_router(api_router,prefix=settings.api_v1_prefix)

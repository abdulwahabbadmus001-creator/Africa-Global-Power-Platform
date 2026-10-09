from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings


class StorageConfigurationError(RuntimeError):
    pass


def _safe_local_path(key: str) -> Path:
    base = Path(settings.storage_local_path).resolve()
    target = (base / key).resolve()
    if target != base and base not in target.parents:
        raise StorageConfigurationError("Unsafe storage key")
    return target


def _s3_client():
    if not all(
        [
            settings.storage_s3_endpoint_url,
            settings.storage_s3_bucket,
            settings.storage_s3_access_key_id,
            settings.storage_s3_secret_access_key,
        ]
    ):
        raise StorageConfigurationError("S3 storage is not fully configured")

    endpoint = settings.storage_s3_endpoint_url.strip().rstrip("/")
    if not endpoint or any(c.isspace() for c in endpoint) or endpoint.count("https://") + endpoint.count("http://") != 1:
        raise StorageConfigurationError("Invalid S3 endpoint URL")
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise StorageConfigurationError("Invalid S3 endpoint URL")
    if settings.environment == "production" and parsed.scheme != "https":
        raise StorageConfigurationError("Production S3 storage must use HTTPS")
    if parsed.hostname and parsed.hostname.endswith(".storage.supabase.co") and parsed.path.rstrip("/") != "/storage/v1/s3":
        raise StorageConfigurationError("Supabase S3 endpoint must end with /storage/v1/s3")

    import boto3
    from botocore.config import Config

    style = "path" if settings.storage_s3_force_path_style else "auto"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=settings.storage_s3_region,
        aws_access_key_id=settings.storage_s3_access_key_id,
        aws_secret_access_key=settings.storage_s3_secret_access_key,
        config=Config(s3={"addressing_style": style}),
    )


def put_private_object(key: str, data: bytes, content_type: str) -> str:
    backend = settings.storage_backend.lower().strip()

    if backend == "local":
        target = _safe_local_path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return "local"

    if backend == "s3":
        client = _s3_client()
        client.put_object(
            Bucket=settings.storage_s3_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl="private, no-store",
        )
        return "s3"

    raise StorageConfigurationError(f"Unsupported storage backend: {backend}")


def get_private_object(key: str, backend: str | None = None) -> bytes:
    selected = (backend or settings.storage_backend).lower().strip()

    if selected == "local":
        target = _safe_local_path(key)
        if not target.exists():
            raise FileNotFoundError(key)
        return target.read_bytes()

    if selected == "s3":
        client = _s3_client()
        response = client.get_object(Bucket=settings.storage_s3_bucket, Key=key)
        return response["Body"].read()

    raise StorageConfigurationError(f"Unsupported storage backend: {selected}")


def delete_private_object(key: str, backend: str | None = None) -> None:
    selected = (backend or settings.storage_backend).lower().strip()

    if selected == "local":
        target = _safe_local_path(key)
        if target.exists():
            target.unlink()
        return

    if selected == "s3":
        client = _s3_client()
        client.delete_object(Bucket=settings.storage_s3_bucket, Key=key)
        return

    raise StorageConfigurationError(f"Unsupported storage backend: {selected}")

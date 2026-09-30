"""Lazily-created S3 client for an S3-compatible bucket (Railway Buckets).

Kept separate + lazy so importing the storage module doesn't require
boto3 or valid S3 creds unless the S3 backend is actually used.

"""

import logging
from functools import lru_cache

from app.core.settings import settings


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_s3_client():
    """Build (once) and return a boto3 S3 client for the configured bucket."""
    import boto3
    from botocore.config import Config

    cfg = settings.s3
    if not (cfg.endpoint and cfg.access_key_id and cfg.secret_access_key and cfg.bucket):
        raise RuntimeError(
            "S3 storage selected but S3 settings are incomplete "
            "(need APP_CONFIG__S3__endpoint / access_key_id / secret_access_key / bucket).",
        )

    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint,
        aws_access_key_id=cfg.access_key_id,
        aws_secret_access_key=cfg.secret_access_key,
        region_name=cfg.region,
        # Railway uses virtual-hosted-style URLs by default; boto3 handles that.
        config=Config(signature_version="s3v4"),
    )

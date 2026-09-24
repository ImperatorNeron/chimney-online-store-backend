"""Media proxy endpoint.

Railway Buckets are PRIVATE — there is no public URL for objects. This
route streams an object back to the browser so the existing /media/<key>
image URLs keep working. Only used when the S3 storage backend is
active; with Supabase the frontend rewrites /media to the public
Supabase CDN and never hits this.

"""

import logging

from fastapi import APIRouter, Response

from app.core.exceptions.common import ItemNotFoundException
from app.services.files import S3FileStorage


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["Media"])

# Cache successfully served media in the browser/CDN for a day. Filenames are
# unique (uuid), so content never changes under a given key.
_CACHE_CONTROL = "public, max-age=86400, immutable"


@router.get("/{key:path}")
async def get_media(key: str):
    storage = S3FileStorage()
    try:
        body, content_type = await storage.get_object(key)
    except Exception as e:  # noqa: BLE001 - boto3 raises ClientError for missing keys
        logger.info("Media not found for key '%s': %s", key, e)
        raise ItemNotFoundException()

    return Response(
        content=body,
        media_type=content_type,
        headers={"Cache-Control": _CACHE_CONTROL},
    )

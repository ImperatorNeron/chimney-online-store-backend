import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.limiter import get_client_ip


logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one line per request for debugging.

    Emits: method, path, status, duration(ms), client IP and a short request id
    (also returned in the `X-Request-ID` response header, so a user-reported
    error can be traced to the exact log line). Unhandled exceptions are logged
    with a full traceback and re-raised so the normal error handling still runs.

    """

    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:8]
        client_ip = get_client_ip(request)
        start = time.perf_counter()

        # Make the id available to downstream handlers if they want it.
        request.state.request_id = request_id

        logger.info(
            "--> %s %s | id=%s | ip=%s",
            request.method,
            request.url.path,
            request_id,
            client_ip,
        )

        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "!!! %s %s | id=%s | ip=%s | unhandled error after %.1fms",
                request.method,
                request.url.path,
                request_id,
                client_ip,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        # 5xx -> error, 4xx -> warning, rest -> info
        if response.status_code >= 500:
            log = logger.error
        elif response.status_code >= 400:
            log = logger.warning
        else:
            log = logger.info
        log(
            "<-- %s %s | id=%s | status=%s | %.1fms | ip=%s",
            request.method,
            request.url.path,
            request_id,
            response.status_code,
            duration_ms,
            client_ip,
        )
        response.headers["X-Request-ID"] = request_id
        return response

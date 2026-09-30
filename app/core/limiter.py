from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """Real client IP for rate limiting behind the nginx reverse proxy.

    The app listens only on localhost inside the same container as
    nginx, so request.client.host is always 127.0.0.1 and useless for
    per-client limits. nginx sets X-Real-IP to the true client address
    ($remote_addr) and appends it to X-Forwarded-For. We trust X-Real-IP
    first (set by our own trusted proxy), then fall back to the first
    X-Forwarded-For hop, then to the socket address. Clients can forge
    these headers, but they can only reach the app through nginx, which
    overwrites X-Real-IP with the real peer address.

    """
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First entry is the original client; the rest are proxies.
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_ip,
    # Generous global ceiling applied to every route via SlowAPIMiddleware.
    # Normal users never hit this; it caps scraping / DoS bursts per IP.
    # Per-route @limiter.limit(...) decorators add stricter limits on top.
    default_limits=["300/minute"],
)

from django.core.cache import cache

HONEYPOT_FIELD = "website"
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 600
RATE_LIMIT_MESSAGE = "Muitas tentativas. Tente novamente em alguns minutos."


def honeypot_triggered(post) -> bool:
    return bool((post.get(HONEYPOT_FIELD) or "").strip())


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or "unknown"


def is_rate_limited(request, scope: str) -> bool:
    key = f"form-rate:{scope}:{client_ip(request)}"
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, RATE_WINDOW_SECONDS)
        count = 1
    return count > RATE_LIMIT

from urllib.parse import quote


def build_whatsapp_url(number: str, message: str = "") -> str:
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if not digits:
        return ""
    url = f"https://wa.me/{digits}"
    if message:
        url = f"{url}?text={quote(message)}"
    return url

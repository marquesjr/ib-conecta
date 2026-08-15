from urllib.parse import quote


def build_whatsapp_url(number: str, message: str = "") -> str:
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if not digits:
        return ""
    url = f"https://wa.me/{digits}"
    if message:
        url = f"{url}?text={quote(message)}"
    return url


def build_whatsapp_share_url(title: str, url: str) -> str:
    page_url = (url or "").strip()
    if not page_url:
        return ""
    heading = (title or "").strip()
    text = f"{heading}\n{page_url}" if heading else page_url
    return f"https://wa.me/?text={quote(text)}"

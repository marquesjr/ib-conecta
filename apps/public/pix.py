"""PIX estático (BR Code) para a página de contribuições.

Monta o texto "copia e cola" no padrão EMV do Banco Central, sem valor e sem
identificador de transação, e o QR Code correspondente em SVG.
"""

import io
import re
import unicodedata

import segno

PIX_GUI = "br.gov.bcb.pix"
MAX_NAME = 25
MAX_CITY = 15
MAX_KEY = 77


def _field(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def _ascii(text: str, limit: int) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    plain = re.sub(r"[^A-Za-z0-9 .\-]", " ", plain)
    return " ".join(plain.split())[:limit].strip()


def normalize_key(key: str, key_type: str = "") -> str:
    key = key.strip()
    digits = re.sub(r"\D", "", key)
    if key_type in ("cpf", "cnpj"):
        return digits
    if key_type == "phone":
        if key.startswith("+"):
            return f"+{digits}"
        if len(digits) in (10, 11):
            return f"+55{digits}"
        return f"+{digits}"
    if key_type in ("email", "random"):
        return key.lower()
    return key


def crc16(payload: str) -> str:
    crc = 0xFFFF
    for byte in payload.encode():
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def pix_payload(key: str, name: str, city: str, key_type: str = "") -> str:
    """Retorna o PIX copia e cola, ou "" se faltar dado obrigatório."""
    key = normalize_key(key, key_type)
    name = _ascii(name, MAX_NAME)
    city = _ascii(city, MAX_CITY)
    if not key or len(key) > MAX_KEY or not name or not city:
        return ""
    payload = (
        _field("00", "01")
        + _field("26", _field("00", PIX_GUI) + _field("01", key))
        + _field("52", "0000")
        + _field("53", "986")
        + _field("58", "BR")
        + _field("59", name)
        + _field("60", city)
        + _field("62", _field("05", "***"))
        + "6304"
    )
    return payload + crc16(payload)


def pix_qr_svg(payload: str) -> str:
    buffer = io.BytesIO()
    segno.make(payload, error="m").save(
        buffer, kind="svg", xmldecl=False, svgns=True, scale=5, border=4, omitsize=True,
        title="QR Code PIX",
    )
    return buffer.getvalue().decode()


def contribution_pix(settings) -> dict:
    payload = pix_payload(
        settings.pix_key,
        settings.pix_beneficiary_name,
        settings.pix_city,
        settings.pix_key_type,
    )
    if not payload:
        return {}
    return {"payload": payload, "qr_svg": pix_qr_svg(payload)}

import unicodedata


def fold(text: str) -> str:
    """Minúsculas e sem acentos, para buscas ("sonia" acha "Sônia")."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()

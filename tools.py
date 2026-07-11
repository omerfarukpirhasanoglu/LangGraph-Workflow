import mimetypes
import requests
from config import CHROMA_API_URL

ALLOWED_TYPES = {".jpg", ".jpeg", ".png", ".webp"}

def call_chroma_model(image_ref: str) -> dict:

    ext = "." + image_ref.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_TYPES:
        raise ValueError(f"Desteklenmeyen dosya türü: {ext}")

    mime_type = mimetypes.guess_type(image_ref)[0]

    with open(image_ref, "rb") as f:
        response = requests.post(
            CHROMA_API_URL,
            files={"file": (image_ref, f, mime_type)},
            timeout=30,
        )
    data = response.json() if response.content else None

    if not response.ok:
        detail = data.get("detail") if data else f"Sunucu hatası: {response.status_code}"
        raise RuntimeError(detail)

    return data
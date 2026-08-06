"""
management/validators.py

Server-side content validation for uploaded files. The frontend's file
picker `accept` attribute (image/jpeg,image/png) is only a UI hint — it
does nothing to stop a request crafted directly against the API with a
renamed or fake-extension file, so every image/passport upload field also
needs a real, content-based check here.
"""

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}


def validate_image_file(value):
    """Rejects anything that isn't a real, Pillow-openable JPEG/PNG image."""
    try:
        img = Image.open(value)
        img_format = img.format
        img.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("Fayl haqiqiy rasm (JPEG yoki PNG) emas.")
    finally:
        value.seek(0)

    if img_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Faqat JPEG yoki PNG formatidagi rasm yuklash mumkin.")


def validate_image_or_pdf_file(value):
    """Passport scans: a real JPEG/PNG image, or a real PDF (checked by
    content — the leading %PDF- magic bytes — not just the extension)."""
    name = (value.name or "").lower()
    if name.endswith(".pdf"):
        header = value.read(5)
        value.seek(0)
        if header != b"%PDF-":
            raise ValidationError("Fayl haqiqiy PDF emas.")
        return

    validate_image_file(value)

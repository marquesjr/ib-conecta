from django.conf import settings
from django.core.files.storage import FileSystemStorage


def private_document_storage():
    return FileSystemStorage(location=str(settings.PRIVATE_MEDIA_ROOT))

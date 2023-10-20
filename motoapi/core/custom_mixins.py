"""
Contains custom mixins.
"""

import uuid
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile


class ResizeImageMixin:
    def resize(self, image_field, size):
        im = Image.open(image_field)
        source_image = im.convert('RGB')
        source_image.thumbnail(size)
        output = BytesIO()
        source_image.save(output, format='JPEG')
        output.seek(0)

        content_file = ContentFile(output.read())
        file = File(content_file)

        random_name = f'{uuid.uuid4()}.jpeg'
        image_field.save(random_name, file, save=False)
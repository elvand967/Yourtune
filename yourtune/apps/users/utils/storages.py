
# ../apps/account/utils/storages.py

from django.core.files.storage import FileSystemStorage
import os

class OverwriteStorage(FileSystemStorage):
    """
    Сторедж, который перезаписывает файл с тем же именем,
    чтобы у пользователя всегда была только одна актуальная аватарка.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
        return name

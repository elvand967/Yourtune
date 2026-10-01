# apps/users/utils/storages.py
# ============================

from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    Локальный storage с перезаписью файла
    при сохранении под тем же именем.
    """

    def get_available_name(self, name, max_length=None):
        """
        Возвращает исходное имя файла.

        Если файл уже существует, он удаляется,
        чтобы новый файл сохранился под тем же именем.
        """
        if self.exists(name):
            self.delete(name)

        return name
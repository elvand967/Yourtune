
# yourtune/apps/core/management/commands/generate_folder_structure.py

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.utils.generate_folder_structure import (
    DEFAULT_NAME_EXCLUSIONS,
    generate_tree_report,
    launch_gui,
)


class Command(BaseCommand):
    help = "Генерирует дерево каталогов в CLI или запускает GUI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["cli", "gui"],
            default="cli",
            help="Режим запуска: cli или gui. По умолчанию cli.",
        )
        parser.add_argument(
            "--base-path",
            type=str,
            default=None,
            help="Базовая директория. По умолчанию берётся из Django settings.",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Путь к файлу отчёта (нужен для cli).",
        )
        parser.add_argument(
            "--exclude-abs",
            nargs="*",
            default=[],
            help="Абсолютные пути для полного исключения.",
        )
        parser.add_argument(
            "--exclude-name",
            nargs="*",
            default=DEFAULT_NAME_EXCLUSIONS,
            help="Имена папок, содержимое которых скрывается.",
        )
        parser.add_argument(
            "--exclude-ext",
            type=str,
            default="",
            help="Исключаемые расширения через ';' или ',' например: .mp3;.torrent;.jpg",
        )
        parser.add_argument(
            "--sort-mode",
            choices=["name", "created", "modified"],
            default="name",
            help="Сортировка директорий: name, created, modified.",
        )
        parser.add_argument(
            "--sort-second-level-only",
            action="store_true",
            help="Сортировать только директории второго уровня относительно base-path.",
        )

    def _get_base_dir(self, base_dir_value):
        if base_dir_value:
            return Path(base_dir_value).resolve()
        return Path(settings.BASE_DIR).resolve()

    def _parse_exts(self, raw: str):
        raw = (raw or "").strip()
        if not raw:
            return []
        parts = raw.replace(",", ";").split(";")
        exts = []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if not p.startswith("."):
                p = f".{p}"
            exts.append(p.lower())
        return exts

    def handle(self, *args, **options):
        mode = options["mode"]
        base_dir_path = self._get_base_dir(options["base_path"])
        output = options["output"]
        exclude_abs = options["exclude_abs"]
        exclude_name = options["exclude_name"]
        exclude_ext = self._parse_exts(options["exclude_ext"])
        sort_mode = options["sort_mode"]
        sort_second_level_only = options["sort_second_level_only"]

        if mode == "cli":
            if not output:
                raise CommandError("Для режима cli нужно указать --output.")

            try:
                lines = generate_tree_report(
                    base_path=str(base_dir_path),
                    abs_exclusions=[str(Path(p).resolve()) for p in exclude_abs],
                    name_exclusions=exclude_name,
                    output_file=output,
                    ext_exclusions=exclude_ext,
                    sort_mode=sort_mode,
                    sort_second_level_only=sort_second_level_only,
                )
            except Exception as e:
                raise CommandError(f"Ошибка генерации дерева каталогов: {e}")

            self.stdout.write(self.style.SUCCESS(f"Отчёт создан: {output}"))
            self.stdout.write("\n".join(lines))
            return

        try:
            launch_gui()
        except Exception as e:
            raise CommandError(f"Не удалось запустить GUI: {e}")

        self.stdout.write(self.style.SUCCESS("GUI завершил работу"))

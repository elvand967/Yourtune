
# apps/core/management/commands/compile_scss.py

from pathlib import Path
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.utils.compiler_scss import compile_scss


class Command(BaseCommand):
    help = "Компилирует SCSS → CSS для приложений проекта"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-dir",
            type=str,
            default=None,
            help="BASE_DIR проекта. По умолчанию берётся из Django settings.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Подробный вывод компиляции.",
        )
        parser.add_argument(
            "--only",
            choices=["core"],
            default=None,
            help="Компилировать только core.",
        )
        parser.add_argument(
            "--app",
            type=str,
            default=None,
            help="Компилировать только указанное приложение.",
        )
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Следить за изменениями SCSS и пересобирать автоматически.",
        )

    def _get_base_dir(self, base_dir_value):
        if base_dir_value:
            return Path(base_dir_value).resolve()
        return Path(settings.BASE_DIR).resolve()

    def _run_once(self, base_dir_path, verbose, only, app):
        try:
            errors_count = compile_scss(
                base_dir_path,
                verbose=verbose,
                only=only,
                app=app,
            )
        except FileNotFoundError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f"Неожиданная ошибка при компиляции SCSS: {e}")

        return errors_count

    def _collect_scss_state(self, base_dir_path):
        apps_dir = base_dir_path / "apps"
        state = {}

        if not apps_dir.exists():
            return state

        for app_path in apps_dir.iterdir():
            if not app_path.is_dir() or app_path.name.startswith("__"):
                continue

            app_name = app_path.name
            scss_path = app_path / "static" / app_name / "scss" / f"{app_name}.scss"
            if scss_path.exists():
                state[str(scss_path)] = scss_path.stat().st_mtime

        return state

    def _watch(self, base_dir_path, verbose, only, app):
        self.stdout.write(self.style.NOTICE("👀 Режим watch включён. Для остановки нажми Ctrl+C."))
        prev_state = self._collect_scss_state(base_dir_path)

        while True:
            try:
                errors_count = self._run_once(base_dir_path, verbose, only, app)

                if errors_count == 0:
                    self.stdout.write(self.style.SUCCESS("SCSS → CSS успешно скомпилирован"))
                else:
                    self.stdout.write(self.style.WARNING(f"Компиляция завершена с ошибками: {errors_count}"))

                while True:
                    time.sleep(1)
                    current_state = self._collect_scss_state(base_dir_path)
                    if current_state != prev_state:
                        prev_state = current_state
                        break

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\nWatch-режим остановлен пользователем."))
                return

    def handle(self, *args, **options):
        base_dir_path = self._get_base_dir(options["base_dir"])
        verbose = options["verbose"]
        only = options["only"]
        app = options["app"]
        watch = options["watch"]

        if only and app:
            raise CommandError("Нельзя использовать --only и --app одновременно. Выбери один режим.")

        if watch:
            self._watch(base_dir_path, verbose, only, app)
            return

        errors_count = self._run_once(base_dir_path, verbose, only, app)

        if errors_count == 0:
            self.stdout.write(self.style.SUCCESS("SCSS → CSS успешно скомпилирован"))
        else:
            self.stdout.write(self.style.WARNING(f"Компиляция завершена с ошибками: {errors_count}"))

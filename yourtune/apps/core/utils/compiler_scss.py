
# apps/core/utils/compiler_scss.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import sass


@dataclass
class CompileResult:
    app_name: str
    scss_path: Path
    css_path: Path
    success: bool
    message: str


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _write_log(log_path: Path, lines: list[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _log(verbose: bool, message: str, log_lines: list[str] | None = None) -> None:
    print(message)
    if log_lines is not None:
        log_lines.append(message)


def _ensure_dir(path: Path, verbose: bool, log_lines: list[str]) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        _log(verbose, f"📁 [created] {path}", log_lines)


def _ensure_placeholder_scss(scss_path: Path, app_name: str, verbose: bool, log_lines: list[str]) -> None:
    if scss_path.exists():
        return

    placeholder = (
        f"// SCSS для приложения {app_name}\n"
        f"// Здесь можно переопределять переменные или добавлять стили.\n\n"
        f"body {{\n"
        f"  // color: #000;\n"
        f"}}\n"
    )
    scss_path.write_text(placeholder, encoding="utf-8")
    _log(verbose, f"📝 [created] {scss_path}", log_lines)


def _compile_one(
    app_name: str,
    scss_path: Path,
    css_path: Path,
    include_paths: list[str],
    output_style: str,
    verbose: bool,
    log_lines: list[str],
    error_logs_dir: Path,
) -> CompileResult:
    try:
        compiled_css = sass.compile(
            filename=str(scss_path),
            output_style=output_style,
            include_paths=include_paths,
        )
        css_path.write_text(compiled_css, encoding="utf-8")
        msg = f"✅ [{app_name}] {scss_path.name} → {css_path.name}"
        _log(verbose, msg, log_lines)
        return CompileResult(app_name, scss_path, css_path, True, msg)

    except sass.CompileError as e:
        msg = f"❌ [{app_name}] Ошибка компиляции {scss_path.name}: {e}"
        _log(verbose, msg, log_lines)

        if css_path.exists():
            _log(verbose, f"🔁 [{app_name}] CSS сохранён без изменений (старая версия)", log_lines)

        error_logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = error_logs_dir / f"{app_name}_scss_error_{_now_stamp()}.log"
        scss_text = scss_path.read_text(encoding="utf-8", errors="replace")
        log_text = (
            f"SCSS file: {scss_path}\n"
            f"CSS file: {css_path}\n"
            f"Error: {e}\n\n"
            f"--- SCSS CONTENT ---\n"
            f"{scss_text}\n"
        )
        log_path.write_text(log_text, encoding="utf-8")
        _log(verbose, f"📄 [{app_name}] Лог ошибки записан: {log_path}", log_lines)

        return CompileResult(app_name, scss_path, css_path, False, msg)


def _iter_apps(apps_dir: Path) -> Iterable[Path]:
    for app_path in sorted(apps_dir.iterdir()):
        if app_path.is_dir() and not app_path.name.startswith("__"):
            yield app_path


def _select_apps(apps_dir: Path, only: str | None, app: str | None) -> list[Path]:
    all_apps = list(_iter_apps(apps_dir))

    if only == "core":
        return [p for p in all_apps if p.name == "core"]

    if app:
        return [p for p in all_apps if p.name == app]

    return all_apps


def compile_scss(
    base_dir: Path,
    verbose: bool = False,
    only: str | None = None,
    app: str | None = None,
) -> int:
    base_dir = Path(base_dir).resolve()
    apps_dir = base_dir / "apps"
    core_partials_path = base_dir / "apps" / "core" / "static" / "core" / "scss" / "partials"
    logs_dir = base_dir / "logs"
    error_logs_dir = logs_dir / "scss_errors"
    run_logs_dir = logs_dir / "scss_compile"

    log_lines: list[str] = []
    errors_count = 0
    results: list[CompileResult] = []

    _log(verbose, "🔧 Запускаем компиляцию SCSS → CSS...", log_lines)
    _log(verbose, f"BASE_DIR: {base_dir}", log_lines)

    if not base_dir.exists():
        raise FileNotFoundError(f"BASE_DIR не найден: {base_dir}")

    if not apps_dir.exists():
        raise FileNotFoundError(f"Папка apps не найдена: {apps_dir}")

    if not core_partials_path.exists():
        _log(verbose, f"⚠️ [warn] Папка глобальных partials не найдена: {core_partials_path}", log_lines)

    _ensure_dir(logs_dir, verbose, log_lines)
    _ensure_dir(run_logs_dir, verbose, log_lines)
    _ensure_dir(error_logs_dir, verbose, log_lines)

    selected_apps = _select_apps(apps_dir, only=only, app=app)

    if only == "core" and not selected_apps:
        raise FileNotFoundError("Приложение core не найдено.")
    if app and not selected_apps:
        raise FileNotFoundError(f"Приложение {app} не найдено.")

    for app_path in selected_apps:
        app_name = app_path.name
        app_static_dir = app_path / "static" / app_name
        scss_dir = app_static_dir / "scss"
        css_dir = app_static_dir / "css"

        _ensure_dir(scss_dir, verbose, log_lines)
        _ensure_dir(css_dir, verbose, log_lines)

        scss_path = scss_dir / f"{app_name}.scss"
        css_path = css_dir / f"{app_name}.css"

        _ensure_placeholder_scss(scss_path, app_name, verbose, log_lines)

        include_paths = [
            str(scss_dir),
            str(core_partials_path),
        ]

        result = _compile_one(
            app_name=app_name,
            scss_path=scss_path,
            css_path=css_path,
            include_paths=include_paths,
            output_style="compressed",
            verbose=verbose,
            log_lines=log_lines,
            error_logs_dir=error_logs_dir,
        )
        results.append(result)

        if not result.success:
            errors_count += 1

    ok_count = len(results) - errors_count
    summary = [
        "",
        "🎉 Компиляция SCSS → CSS завершена успешно." if errors_count == 0
        else f"❌ Компиляция SCSS → CSS завершена с ошибками: {errors_count}",
        f"✅ Успешно: {ok_count}",
        f"❌ Ошибок: {errors_count}",
    ]
    for line in summary:
        _log(verbose, line, log_lines)

    run_log_path = run_logs_dir / f"scss_compile_{_now_stamp()}.log"
    _write_log(run_log_path, log_lines + summary)
    _log(verbose, f"📄 Общий лог записан: {run_log_path}", log_lines)

    return errors_count

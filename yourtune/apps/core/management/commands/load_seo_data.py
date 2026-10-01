
# apps/core/management/commands/load_seo_data.py

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.core.models.seo import StopWord, SEOReplacement


class Command(BaseCommand):
    help = "Load SEO stop words and replacements from JSON files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--stop-words",
            default="apps/core/utils/stop_words.json",
            help="Path to stop_words.json",
        )
        parser.add_argument(
            "--replacements",
            default="apps/core/utils/seo_replacements.json",
            help="Path to seo_replacements.json",
        )

    def handle(self, *args, **options):
        self.load_stop_words(Path(options["stop_words"]))
        self.load_replacements(Path(options["replacements"]))

    def load_stop_words(self, path: Path):
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Stop words file not found: {path}"))
            return

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            obj, created = StopWord.objects.get_or_create(
                lang=entry["lang"].lower(),
                word=entry["word"].lower(),
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added stop word: [{obj.lang}] {obj.word}"))

    def load_replacements(self, path: Path):
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"SEO replacements file not found: {path}"))
            return

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for entry in data:
            obj, created = SEOReplacement.objects.get_or_create(
                source_word=entry["source_word"].lower(),
                defaults={"replacement": entry["replacement"].lower()},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added SEO replacement: {obj.source_word} → {obj.replacement}"))
            elif obj.replacement != entry["replacement"].lower():
                obj.replacement = entry["replacement"].lower()
                obj.save(update_fields=["replacement"])
                self.stdout.write(self.style.SUCCESS(f"Updated SEO replacement: {obj.source_word} → {obj.replacement}"))
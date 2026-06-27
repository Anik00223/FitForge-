#!/usr/bin/env python
"""Django management entry-point.

The settings module is resolved in this order:

1. ``DJANGO_SETTINGS_MODULE`` environment variable (preferred for
   production / CI).
2. ``--settings`` command-line flag.
3. ``config.settings.development`` (the safe local default).
"""
import os
import sys


def main() -> None:
    if "test" in sys.argv:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover - import guard
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and the "
            "virtual environment is activated."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

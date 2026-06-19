"""Contains the NDR Core app configuration."""
from django.apps import AppConfig


class NdrCoreConfig(AppConfig):
    """NDR Core app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ndr_core'

    def ready(self):
        import ndr_core.signals  # noqa: F401 — registers signal handlers

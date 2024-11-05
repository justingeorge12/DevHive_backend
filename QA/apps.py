from django.apps import AppConfig


class QaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'QA'


    def ready(self) -> None:
       import QA.signal

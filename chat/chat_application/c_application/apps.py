from django.apps import AppConfig


class CApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'c_application'
    
    def ready(self):
        import c_application.signals

from django.apps import AppConfig


class UserAppConfig(AppConfig):
    name = 'apps.users'
    label = 'users'
    verbose_name = 'Users'

    def ready(self):
        import apps.users.signals

# This is how we register our custom app config with Django. Django is smart
# enough to look for the `default_app_config` property of each registered app
# and use the correct app config based on that value.
default_app_config = 'apps.users.UserAppConfig'
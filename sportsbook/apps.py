from django.apps import AppConfig

class SportsbookConfig(AppConfig):
    name = 'sportsbook'
    verbose_name = 'Sportsbook App'

    def ready(self):
        """
        Import signal handlers. From the Django 2.0 docs:

        In practice, signal handlers are usually defined in a signals submodule
        of the application they relate to. Signal receivers are connected in
        the ready() method of your application configuration class. If you're
        using the receiver() decorator, simply import the signals submodule
        inside ready().

        Also, see this discussion thread:
        http://stackoverflow.com/questions/7115097/
            the-right-place-to-keep-my-signals-py-files-in-django
        """
        import sportsbook.signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from sportsbook.models import Odds


@receiver(post_save, sender=Odds, dispatch_uid='sportsbook_calculate_arb')
def calculate_arb(sender, instance, **kwargs):
    """
    Args:
        sender [Odds]: Class of the signal being received.
        instance [Odds]: Model instance of the signal being received.
        kwargs [dict]: Example: {
            'update_fields': None,
            'raw': False,
            'signal': <django.db.models.signals.ModelSignal>,
            'using': 'default',
            'created': False
        }
    """
    results = instance.arb(delta=120)
    #print 'calculate_arb %s: %s' % (instance, results)

from django.contrib import admin

# Register your models here.
from .models import Player
from .models import Team

admin.site.register(Player)
admin.site.register(Team)
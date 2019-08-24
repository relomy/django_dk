from django.urls import path

from . import views

urlpatterns = [
    # ex: /nba/
    path("", views.index, name="index"),
    # ex: /nba/<player_id>
    path("<int:player_id>/", views.detail, name="detail"),
]

from django.http import Http404
from django.shortcuts import render

from .models import Player

# Create your views here.
def index(request):
    # top_five_seasons = Player.objects.order_by('-seasons')[:5]
    # for p in top_five_seasons:
    #     print(f"{p}: {p.seasons} seasons")
    # output = '|'.join(([str(p.seasons) for p in top_five_seasons if p.seasons]))
    top_five_seasons = Player.objects.order_by("-seasons")[:5]
    context = {"top_five_seasons": top_five_seasons}
    return render(request, "nba/index.html", context)


def detail(request, player_id):
    try:
        player = Player.objects.get(nba_id=player_id)
    except Player.DoesNotExist:
        raise Http404("Player does not exist")
    return render(request, "nba/detail.html", {"player": player})

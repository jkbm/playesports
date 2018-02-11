from django.shortcuts import render
from django.http import HttpResponse
from .models import Team, Player, Tournament, Match
from django.contrib import messages

# Create your views here.
def home(request):
    teams = Team.objects.all()

    return render(request, "csapp/teams.html", {"teams": teams})
def temp(request):

    return HttpResponse('Hello, world! This is CS GO part of the web-site')

def teams_list(request):

    teams = Team.objects.all()

    return render(request, "csapp/teams.html", {"teams": teams})

def team_detail(request, pk):

    team = Team.objects.get(pk=pk)
    players = Player.objects.filter(team=team)

    return render(request, "csapp/team.html", {"team": team,
                                               "players": players})

def search(request):
    """
    Search page view
    """

    try:
        query = request.GET.get('query')
        if len(query) < 3:
            messages.warning(request, "Search query must be at least 4 characters.")
            query = "NONE"
    except:
        query = "NONE"


    teams = Team.objects.filter(name__icontains=query)
    players = Player.objects.filter(name__icontains=query)
    tournaments = Tournament.objects.filter(title__icontains=query)

    return render(request, "csapp/search.html", {"teams": teams,
                                                 "players": players,
                                                 "tournaments": tournaments})

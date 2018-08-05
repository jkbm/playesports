# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Tournament, Match, Player, Game, Group, Card, Deck, Deckset
from .forms import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from django.views import View
from braces.views import LoginRequiredMixin
from .extras import get_top, get_cards, get_names, add_cards
from .utils import get_stats, Uploader
from .misc import import_cards

from .serializers import PlayerSerializer, TournamentSerializer, MatchSerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView 

# Create your views here.
def index(request):
    """
    App home page view
    """
    tournaments = Tournament.objects.filter(
        end_date__lte=timezone.now()).order_by(
            '-end_date')
    matches = Match.objects.filter(
        date__lte=timezone.now()).order_by(
            '-date')
    matches = matches[:10]
    upcoming_matches = Match.objects.filter(
        date__gte=timezone.now()).order_by(
            'date')
    upcoming_matches = upcoming_matches[:5]

    players = Player.objects.all()
    top_players = get_top(players)

    posts = Post.objects.all().order_by(
            '-date')[:15]

    return render(request, 'hsapp/index.html', {'tournaments': tournaments[:5],
                                                'matches': matches,
                                                'upcoming_matches': upcoming_matches,
                                                'players': top_players,
                                                'posts': posts})

def tournament_list(request):
    """
    Tournaments list page
    """
    tournaments = Tournament.objects.filter(
        end_date__lte=timezone.now(), winner__isnull=False).order_by(
            '-end_date')
    tournaments_future = Tournament.objects.filter(
        end_date__gte=timezone.now()).order_by(
            'end_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(tournaments, 5)
    try:
        tournament_pages = paginator.page(page)
    except PageNotAnInteger:
        tournament_pages = paginator.page(1)
    except EmptyPage:
        tournament_pages = paginator.page(paginator.num_pages)
    return render(request, 'hsapp/tournament_list.html', {'tournaments': tournament_pages,
                                                          'tournaments_future': tournaments_future})

def tournament_detail(request, pk):
    """
    Tournament details view
    """
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = Match.objects.filter(tournament=tournament, finished=True).reverse()
    upcoming_matches = Match.objects.filter(tournament=tournament, finished=False)
    players = tournament.players.all()
    if tournament.winner:
        day = ""
    else:
        today = timezone.now().date()
        start = tournament.start_date
        diff = today - start
        diff = diff.days + 1
        day = "Day {0}".format(diff)
    return render(request, 'hsapp/tournament_detail.html', {'tournament': tournament, 'day': day,
                                                            'matches': matches, 'players': players,
                                                            'upcoming_matches': upcoming_matches})

@login_required
def tournament_add(request):
    """
    Add new tournament with form view
    """
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            tournament.save()
            if 'save' in request.POST:
                messages.info(request, 'Tournament created.')
                return redirect('hs:tournament_edit', pk=tournament.pk)
            elif 'group' in request.POST:
                return redirect('hs:group_add', pk=tournament.pk)
            elif 'match' in request.POST:
                return redirect('hs:match_add', pk=tournament.pk)
            elif 'delete' in request.POST:
                tournament.delete()
                return redirect('hs:tournament_list')
    else:
        form = TournamentForm()

    return render(request, 'hsapp/tournament_add.html', {'form': form})

@login_required
def tournament_edit(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            tournament = form.save()
            tournament.save()
            if 'save' in request.POST:
                return redirect('hs:tournament_detail', pk=tournament.pk)
            elif 'group' in request.POST:
                return redirect('hs:group_add', pk=tournament.pk)
            elif 'match' in request.POST:
                return redirect('hs:match_add', pk=tournament.pk)
            elif 'delete' in request.POST:
                tournament.delete()
                return redirect('hs:tournament_list')
    else:
        form = TournamentForm(instance=tournament)

    return render(request, 'hsapp/tournament_add.html', {'form': form})

@login_required
def group_add(request, pk):
    tournament = Tournament.objects.get(pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, tournament=tournament)
        if form.is_valid():
            group = form.save()
            group.save()
    else:
        form = GroupForm(initial={"tournament": tournament}, tournament=tournament)

    return render(request, 'hsapp/group_add.html', {'form': form})

def tournament_unfinished(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    matches = Match.objects.filter(tournament=tournament, finished=False)
    players = tournament.players.all()
    return render(request, 'hsapp/tournament_detail.html', {'tournament': tournament, 'matches': matches, 'players': players})

def tournament_bracket(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    groups = Group.objects.filter(tournament=tournament).order_by('letter')
    finals = Match.objects.filter(stage='Finals', tournament=tournament)
    semifinals = Match.objects.filter(stage='Semifinals', tournament=tournament)
    quarterfinals = Match.objects.filter(stage='Quarterfinals', tournament=tournament)
    oneeight = Match.objects.filter(stage='oneeight', tournament=tournament)
    more=[]
    tabledata = []
    for group in groups:
        data = group.get_table_data()        
        tabledata.append([group, data])
    more.append(range(0, 8-len(oneeight)))
    more.append(range(0, 4-len(quarterfinals)))
    more.append(range(0, 2-len(semifinals)))
    more.append(range(0, 1-len(finals)))
    return render(request, 'hsapp/tournament_bracket.html', {'tournament': tournament,
                                                            'finals': finals, 'semifinals': semifinals,
                                                            'quarterfinals': quarterfinals, 'more': more,
                                                            'tabledata': tabledata})
                      
def players_list(request):
    players = Player.objects.order_by('name').all()
    return render(request, 'hsapp/players_list.html', {'players': players})

def player_detail(request, pk):
    player = Player.objects.get(pk=pk)
    matches = Match.objects.filter(Q(player1=player) | Q(player2=player)).order_by(
            '-date')
    tournaments = []
    form = []
    for match in matches[:5]:
        if match.winner == player:
            form.append("W")
        else:
            form.append("L")
    
    stats = get_stats(player)
    print(stats)
    for match in matches:
        if match.tournament in tournaments:
            pass
        else:
            tournaments.append(match.tournament)
    return render(request, 'hsapp/player_detail.html',
                  {'player': player,
                   'tournaments': tournaments,
                   'matches': matches[:5],
                   'form': form,
                   'stats': stats,
                  })

@login_required
def player_add(request, pk=0):
    """
    Add new player to database
    """
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            player = form.save()
            player.save()
            return redirect('hs:player_detail', pk=player.pk)
    else:
        form = PlayerForm
    return render(request, 'hsapp/player_add.html', {'form': form})

def match_detail(request, pk):
    """
    Match details page
    """
    match = Match.objects.get(pk=pk)
    games = Game.objects.filter(match=match)
    decks1 = Deck.objects.filter(player=match.player1, tournament=match.tournament)
    decks2 = Deck.objects.filter(player=match.player2, tournament=match.tournament)
    match_info = {}
    i = 1
    for game in games:
        if game.winner == game.player1:
            match_info['game%s'%i] = '{0}v{1}. Winner: {2}({3})'.format(
                game.class1, game.class2, game.winner, game.class1)
            i += 1
        else:
            match_info['game%s'%i] = '{0}v{1}. Winner: {2}({3})'.format(
                game.class1, game.class2, game.winner, game.class2)
            i += 1
    return render(request, 'hsapp/match_detail.html', {'match': match, 'games': games,
                                                       'decks1': decks1, 'decks2': decks2
                                                      })

@login_required
def like_match(request):
    if request.method == 'GET':
        match_pk = request.GET.get('match_pk')
    likes = 0
    if match_pk:
        match = Match.objects.get(pk=match_pk)
        if match:
            likes = match.likes + 1
            match.likes = likes
            match.save()
    return HttpResponse(likes)

def match_list(request, pk, **kwargs):
    """
    Matches list per tournament and/or group
    """
    tournament = Tournament.objects.get(pk=pk)
    for name, value in kwargs.items():
        if name == 'group':
            group = Group.objects.get(tournament=tournament, letter=value)
            players = group.players.all()
            matches = Match.objects.filter(stage='Groups', tournament=tournament)
            matches = matches.filter(Q(player1__in=players) | Q(player2__in=players))
            info = 'Matches for group {0} of {1} tournament'.format(value, tournament.title)
    if matches:
        pass
    else:
        info = 'Matches of {0} tournament'.format(tournament.title)
        matches = Match.objects.filter(tournament=tournament)
    return render(request, 'hsapp/match_list.html', {'matches': matches, 'info': info})

@login_required
def match_add(request, pk=0):
    """
    Add new match to the tournament
    """
    if pk != 0:
        tournament = Tournament.objects.get(pk=pk)
    else:
        tournament = Tournament.objects.none()
        tournament.date = timezone.now()
    if request.method == 'POST':
        form = MatchForm(request.POST, tournament=tournament)
        if form.is_valid():
            match = form.save()
            match.save()
            if 'save' in request.POST:
                return redirect('hs:tournament_detail', pk=match.tournament.pk)
            elif 'add-more' in request.POST:
                return redirect('hs:match_add', pk=match.tournament.pk)
    else:
        form = MatchForm(initial={"tournament": tournament, "date": tournament.start_date},
                         tournament=tournament)
    return render(request, 'hsapp/match_add.html', {'form': form})

@login_required
def game_add(request, match=0):
    """
    Add new match to the tournament
    """
    if match != 0:
        match = Match.objects.get(pk=match)
    else:
        match = Match.objects.none()

    if request.method == 'POST':
        form = GameForm(request.POST, match=match)
        if form.is_valid():
            game = form.save()
            game.save()
            if 'save' in request.POST:
                return redirect('hs:match_detail', pk=game.match.pk)
            elif 'add-more' in request.POST:
                return redirect('hs:game_add', match=game.match.pk)
    else:
        form = GameForm(initial={"match": match}, match=match)

    return render(request, 'hsapp/game_add.html', {'form': form})

@login_required
def control_panel(request):
    """
    Control panel page for adding and modifying app data
    """
    if request.method == 'POST':
        form = ControlPanelForm(request.POST)
        if form.is_valid():
            tournament = form.cleaned_data['tournament']
            if 'add-group' in request.POST:
                return redirect('hs:group_add', pk=tournament.pk)
            elif 'edit-group' in request.POST:
                return redirect('hs:group_add', pk=tournament.pk)
            elif 'edit-tournament' in request.POST:
                return redirect('hs:tournament_edit', pk=tournament.pk)
            
    else:
        form = ControlPanelForm()

    return render(request, 'hsapp/control_panel.html', {'form': form})

def cards(request, card_set=1001):
    CARD_SETS = {'2': 'Basic', '3': 'Expert', '4': 'Hall of Fame', '5': 'Classic',
                 '12': 'Naxxramas', '13': 'Goblins vs Gnomes',
                 '14': 'Blackrock Mountain', '15': 'The Grand Tournament',
                 '16': 'League of Explorers', '17': 'Heroes', '18': "Powers",
                 '20': 'League OF Explorers', '21': 'Whispers of the Old Gods',
                 '23': 'One Night in Karazhan', '24': 'One Night in Karazhan',
                 '25': 'Mean Streets of Gadgetzan', '27': "Journey to Un'Goro",
                 '1001': 'Knights of the Frozen Throne', '2002': "The Boomsday Project",
                 '2003': 'The Witchwood', '2004': 'Kobolds & Catacombs', }
    CLASSES = {'12': 'Neutral', '10': 'Warrior',
               '2': 'Druid', '3': 'Hunter', '4': 'Mage', '5': 'Paladin',
               '6': 'Priest', '7': 'Rogue', '8': 'Shaman', '9': 'Warlock'}
    RARITY = {'1': 'Basic', '2': 'Common', '3': 'Rare', '4': 'Epic', '5': 'Legendary'}

    card_set = CARD_SETS[str(card_set)]
    cards_all = Card.objects.filter(card_set=card_set)
    cards_dict = {}
    for k in CLASSES:
        all_rarities = {}
        for r in RARITY:
            all_rarities[RARITY[r]] = cards_all.filter(rarity=RARITY[r],
                                                       CLASS=CLASSES[k]).order_by('cost')
        cards_dict[CLASSES[k]] = all_rarities

    return render(request, 'hsapp/cards.html', {'cards': cards_dict})

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


    cards = Card.objects.filter(name__icontains=query)
    players = Player.objects.filter(name__icontains=query)
    tournaments = Tournament.objects.filter(title__icontains=query)

    return render(request, "hsapp/search.html", {"cards": cards,
                                                 "players": players,
                                                 "tournaments": tournaments})

def about(request):
    """
    About page view
    """
    return redirect('core:nopage')

class FeedbackView(LoginRequiredMixin, View):
    """
    Feedback page view
    """
    def get(self, request):
        """
        Get request method
        """
        form = FeedbackForm()
        return render(request, 'hsapp/feedback.html', {'form': form})

    def post(self, request):
        """
        Post request method
        """
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            messages.info(request, 'Thank you for your feedback, {0}!'.format(name))
            return redirect('hs:index')

class AddPost(LoginRequiredMixin, View):
    """
    Add new post to posts feed
    """
    def get(self, request):
        """
        Get request method
        """
        form = AddPostForm()
        return render(request, 'hsapp/addpost.html', {'form': form})

    def post(self, request):
        """
        Post request method
        """
        form = AddPostForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            post = Post.objects.create(title=form['title'], tags=form['tags'],
                                       article=form['article'])
            post.save()
            messages.info(request, 'Post added!')
            return redirect('hs:index')
        else:
            messages.info(request, 'Error in form: {0}'.format(form.errors))
            return render(request, 'hsapp/addpost.html', {'form': form})

class EditPost(LoginRequiredMixin, View):
    """
    Edit exising post to posts feed
    """
    def get(self, request, pk):
        """
        Get request method
        """
        post = Post.objects.get(pk=pk)
        form = AddPostForm(initial = {'title': post.title, 'tags': post.tags, 'article': post.article })
        return render(request, 'hsapp/addpost.html', {'form': form})

    def post(self, request, pk):
        """
        Post request method
        """
        post = Post.objects.get(pk=pk)
        form = AddPostForm(request.POST)
        if form.is_valid():
            form = form.cleaned_data
            post.title = form['title']
            post.tags = form['tags']
            post.article = form['article']
            post.save()
            messages.info(request, 'Post added!')
            return redirect('hs:index')
        else:
            messages.info(request, 'Error in form: {0}'.format(form.errors))
            return render(request, 'hsapp/addpost.html', {'form': form})

def post_detail(request, pk):
    """
    Post detail page view
    """
    post = Post.objects.get(pk=pk)
    tags = post.tags
    tags = tags.replace(', ', ',')
    tags = tags.split(',')
    print(tags)
    rtags = {}
    for tag in tags:
        rtag = tag
        rtag = rtag.replace(' ', '_')
        rtags[tag] = rtag

    print(rtags)

    return render(request, 'hsapp/article.html', {'post': post, 'tags': rtags})

def post_list(request, tag=None):

    if tag:
        posts = Post.objects.filter(tags__icontains=tag)
    else:
        posts = Post.objects.all()

    return render(request, 'hsapp/articles.html', {'posts': posts})



def temp(request):
    """
    Temporary view
    """
    #link = "https://us.battle.net/hearthstone/en/esports/tournament/hct-summer-championship-2017"
    link = "https://playhearthstone.com/en-gb/esports/tournament/hct-world-championship-amsterdam"
    tpk = 30
    #import_cards()
    """
    uploader = Uploader(link, tpk, True)
    uploader.get_data()
    uploader.clear_nones()
    uploader.get_players()
    #uploader.add_group_matches()
    #uploader.add_playoff_matches()
    """
    return render(request, 'hsapp/temp.html')

"""
    API PORTION OF VIEWS
"""
class PlayerCreateReadView(ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'name'

class PlayerReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'name'

class TournamentCreateReadView(ListCreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    lookup_field = 'pk'

class TournamentReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    lookup_field = 'pk'

class MatchCreateReadView(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    lookup_field = 'pk'

class MatchReadUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    lookup_field = 'pk'

from django.db.models import Q

import requests
import urllib.request
import json
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from .models import Match, Tournament, Player, Game, Group, Deck, Deckset
from django.core.files import File 

class Uploader():
    """
        Class for automatic data upload from given source.
    """
    
    def __init__(self, link, tpk, groups=True):
        self.link = link
        self.tpk = tpk
        self.tournament = Tournament.objects.get(pk=tpk)
        self.groups = groups

    def get_data(self):
        """Get data from web-source"""
        page = requests.get(self.link)
        soup = BeautifulSoup(page.text, 'html.parser')
        scripts = soup.find_all('script', type="text/javascript")
        data = scripts[4].string
        print(data[:30])
        result = re.search('\tdata:(.*?)"1.0.0"},', data).groups()
        result = result[0]+'"1.0.0"}'
        jresult = json.loads(result)
        if self.groups:
            playoffs = jresult['stages'][1]['brackets'][0]['matches']
            self.playoffs = sorted(playoffs, key=lambda d: (d['round'], d['ordinal']))
            self.groups = jresult['stages'][0]['brackets']
            self.players = jresult['competitors']
            return self.playoffs, self.groups, self.players
        else:
            playoffs = jresult['stages'][0]['brackets'][0]['matches']
            self.playoffs = sorted(playoffs, key=lambda d: (d['round'], d['ordinal']))
            self.players = jresult['competitors']
            return self.playoffs, self.players

        print("Got data.")


    def add_group_matches(self, tpk=15):
        """Add group stage matches to DB"""
        for group in self.groups:
            self.add_matches(group['matches'], bracket_stage="Groups")

    def add_group(self, group):
        """Define groups for the tournament"""
        cgroup = Group.objects.create(tournament=self.tournament, letter=group['name'][-1])
        for p in group['rankings']['content']:
            player = Player.objects.get(name=p['competitor']['name'])
            cgroup.players.add(player)

    def add_playoff_matches(self, tpk=15):
        """Add playoff matches to DB"""
        self.add_matches(self.playoffs)

    def add_matches(self, matches, bracket_stage="Playoffs"):
        """Add matches and games from given data to DB"""
        # Add or update matches
        for match in matches:
            try:
                competitors = match['competitors']

                #timestamp = match.get('startDate') or match.get('endDate') or match.get('dateFinished') or time.mktime(self.tournament.start_date.timetuple())*1e3
                #date = datetime.fromtimestamp(timestamp / 1e3)

                date = self.tournament.start_date
                for idx, val in enumerate(competitors):
                    if val is None:
                        competitors[idx] = {'name': 'None'}
                player1 = Player.objects.get(name=competitors[0]['name'])
                player2 = Player.objects.get(name=competitors[1]['name'])
                
                score = "{0}-{1}".format(match['scores'][0]['value'], match['scores'][1]['value'])
                form = "Best of " + str(match['bestOf'])
                round = match['round']
                if match['state'] == 'CONCLUDED':
                    finished = True
                else:
                    finished = False
                rounds = {1: 'Quarterfinals', 2: 'Semifinals', 3: 'Finals'}
                if bracket_stage == "Playoffs":
                    stage = rounds[match['round']]
                else:
                    stage = bracket_stage
                try:
                    vod_link = match['vodLink']
                except:
                    vod_link = ""
                #Create the object if doesnt exist
                obj, created = Match.objects.get_or_create(player1=player1, player2=player2,
                                                           stage=stage, tournament=self.tournament,
                                                           round=round)
                obj.score = score
                obj.format = form
                obj.date = date
                if finished:
                    obj.winner = Player.objects.get(name=match['winner']['name'])
                    obj.finished = finished
                obj.save()
                print('Created: {0}-{1}'.format(obj, created))
                self.add_games(obj, match)
            except Exception as e:
                print(match, e)
                print('\n')


    def add_games(self, match, data):
        """Add games from the match to DB"""
        p1 = match.player1
        p2 = match.player2
        for g in data['games']:
            c1 = g['attributes']['competitor1Class']
            c2 = g['attributes']['competitor2Class']
            if g['points'] == [0, 1]:
                winner = p2
            elif g['points'] == [1, 0]:
                winner = p1
            game = Game.objects.get_or_create(match=match, player1=p1, player2=p2, 
                                            class1=c1, class2=c2, winner=winner)  

    def get_players(self):
        """Add players that participate in the tournament,
        create them if they are not in the DB"""

        base = "esports\media\HSapp\players\\"
        for p in self.players:
            try:
                obj, created = Player.objects.get_or_create(name=p['competitor']['name'])

                file_name = "{0}.jpg".format(p['competitor']['name'])
                try:
                    r = requests.get(p['competitor']['headshot'])
                except Exception as e:
                    print(e)
                    r = requests.get("https://d2q63o9r0h0ohi.cloudfront.net/images/media/artwork/artwork1-full-e2b8aa5b1470484b8f8a67022ac2364830e8a5511ca56d6ab00dbe1785413e46fbb919bd95be8df710a6d411bb332cd212ec31190e1d3a7a2d7acc58fc1149fb.jpg")
                with open(base+"/tmp/temp.png", "wb") as f:
                    f.write(r.content)
                reopen = open(base+"/tmp/temp.png", "rb")
                django_file = File(reopen)
                try:
                    obj.country = p['competitor']['nationality']
                except:
                    print("No country")
                obj.image.save(file_name, django_file, save=True)
                obj.save()

                self.tournament.players.add(obj)
                print(obj, created)
            except Exception as e:
                print('Failed' + e)

    def clear_nones(self):    
        """Delete matches with undecided opponents
        """
        none_player = Player.objects.get(name="None")
        none_matches = Match.objects.filter(Q(player1=none_player) | Q(player2=none_player),
                                            tournament=self.tournament)
        for m in none_matches:
            m.delete()

    def get_decks(self):
        base = "esports\media\HSapp\decks\\"
        html = requests.get("https://playhearthstone.com/en-us/blog/21101731/here-are-your-hct-summer-championship-deck-lists-10-5-17")
        soup = BeautifulSoup(html.text, 'html.parser')
        tabs = soup.find_all(class_="tab-pane")
        for t in range(0, len(tabs), 4):
            name = self.longestSubstringFinder(tabs[t].get('id'), tabs[t+1].get('id'))         
            player = Player.objects.get(name__iexact=name)
            deckset = Deckset.objects.create(player=player, tournament=self.tournament)
            for c in range(0, 4):
                deck_class = tabs[t+c].get('id').replace(name, "").upper()
                file_name = "{0}{1}.png".format(self.tournament.pk, tabs[t+c].get('id'))
                deck = Deck.objects.create(player=player, deck_class=deck_class,
                                           tournament=self.tournament)
                r = requests.get(tabs[t+c].img.get('src'))
                with open(base+"\tmp\temp.png", "wb") as f:
                    f.write(r.content)
                reopen = open(base+"\tmp\temp.png", "rb")
                django_file = File(reopen)
                deck.image.save(file_name, django_file, save=True)
                deck.save()            
                deckset.decks.add(deck)
            deckset.save()

    def longestSubstringFinder(string1, string2):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    if (len(match) > len(answer)): answer = match
                    match = ""
        return answer



def get_stats(player):
    classes = {'Mage': 0, 'Warrior':0, 'Warlock': 0, 'Hunter': 0, 'Priest': 0,
               'Druid': 0, 'Rogue': 0, 'Paladin': 0, 'Shaman': 0}
    stats = {'wins': 0, 'loses': 0, 'gwins': 0, 'gloses': 0, 'classes': classes}
    matches = Match.objects.filter(Q(player1=player) | Q(player2=player))

    for match in matches:
        games = Game.objects.filter(match=match)
        if match.winner == player:
            stats['wins'] += 1
        elif match.winner != player:
            stats['loses'] += 1
        
        for game in games:
            if game.winner == player:
                stats['gwins'] += 1
                if game.winner == game.player1:
                    class__= game.class1.lower().capitalize()
                    classes[class__] += 1
            elif game.winner != player:
                stats['gloses'] += 1

    return stats        

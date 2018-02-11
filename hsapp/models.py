# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models
from django.urls import reverse 
from django_countries.fields import CountryField
from django.utils import timezone
# Create your models here.

class Player(models.Model):
    """Class for competitive HS players"""
    name = models.CharField(max_length=200, unique=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    team = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='hsapp/players',
                              default='media/hsapp/players/user-icon-placeholder_DP8A4SZ.png',
                              null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_screen_name(self):
        words = self.fullname.split()
        lenght = len(words) - 1
        words.insert(lenght, "'" + self.name + "'")
        return ' '.join(words)

    def get_absolute_url(self):
        """Get absolute url for REST API"""
        return reverse("hs:player_detail", kwargs={"pk": self.pk})


class Tournament(models.Model):
    """Tournament class"""
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    prize = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, related_name='players')
    presenters = models.ManyToManyField(Player, related_name='presenters')
    groups = models.BooleanField(default=False)
    about = models.TextField(null=True, blank=True)
    format = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='hsapp/tournaments', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_location(self):
        """Format location to display"""
        location = "{0}, {1}".format(self.city, self.country.name)
        return location

    def get_absolute_url(self):
        """Get absolute url for REST API"""
        return reverse("hs:tournament_detail", kwargs={"pk": self.pk})

class Match(models.Model):
    """ Match object for DB. Contains all necessery information
    regarding given match.
    """

    class Meta:
        verbose_name_plural = "Matches"

    STAGES = (
        ('FINALS', 'Finals'),
        ('SEMIFINALS', 'Semifinals'),
        ('QUARTERFINALS', 'Quarterfinals'),
        ('GROUP STAGE', 'Group stage'),
        ('PLAYOFFS', 'Playoffs')
    )
    date = models.DateField(default=timezone.now)
    time = models.DateTimeField(null=True, blank=True)
    player1 = models.ForeignKey(Player, related_name='p1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='p2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Player, related_name='win', null=True, blank=True, on_delete=models.CASCADE)
    score = models.CharField(max_length=10, default='0-0')
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=100, null=True, blank=True)
    stage = models.CharField(max_length=100, null=True, blank=True)
    round = models.IntegerField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE)
    vod_link = models.CharField(max_length=200, null=True, blank=True)
    likes = models.IntegerField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        score = self.score.split('-')
        self.score1 = score[0]
        self.score2 = score[1]
        if int(self.score1) > int(self.score2):
            self.winner = self.player1
        elif int(self.score1) < int(self.score2):
            self.winner = self.player2
        super(Match, self).save(*args, **kwargs)

    def __str__(self):
        if self.finished is True:
            matchtitle = "{0}: {1} {2} {3}".format(self.tournament.title,
                                                   self.player1, self.score, self.player2)
        else:
            if self.player1.name != "None" or self.player2.name != "None":
                matchtitle = "{0}: {1} - {2}".format(self.tournament.title,
                                                     self.player1, self.player2)
            else:
                matchtitle = "{0}: {1}".format(self.tournament.title, self.stage)

        return matchtitle

    def short_title(self):
        if self.finished == True:
            matchtitle = "{0} {1} {2}".format(self.player1, self.score, self.player2)
        else:
            if self.player1.name != "None" or self.player2.name != "None":
                matchtitle = "{0} - {1}".format(self.player1, self.player2)
            else:
                matchtitle = "{0}".format( self.stage)
            

        return matchtitle

    def get_absolute_url(self):
        """Get absolute url for REST API"""
        return reverse("hs:match_detail", kwargs={"pk": self.pk})

class Game(models.Model):

    CLASSES = (
        ('MAGE', 'Mage'),
        ('WARRIOR', 'Warrior'),
        ('WARLOCK', 'Warlock'),
        ('HUNTER', 'Hunter'),
        ('PRIEST', 'Priest'),
        ('DRUID', 'Druid'),
        ('ROGUE', 'Rogue'),
        ('PALADIN', 'Paladin'),
        ('SHAMAN', 'Shaman')
    )
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Player, related_name='pl1', null=True, on_delete=models.CASCADE)
    player2 = models.ForeignKey(Player, related_name='pl2', null=True, on_delete=models.CASCADE)
    class1 = models.CharField(max_length=50, choices=CLASSES)
    class2 = models.CharField(max_length=50, choices=CLASSES)
    winner = models.ForeignKey(Player, related_name='winner', null=True, on_delete=models.CASCADE)

    def __str__(self):
        gamename = "{0}({1}) vs {2}({3})".format(self.match.player1.name,
                                                 self.class1, self.match.player2.name, self.class2)
        return gamename

    def save(self, *args, **kwargs):
        self.player1 = self.match.player1
        self.player2 = self.match.player2
        super(Game, self).save(*args, **kwargs)

class Group(models.Model):

    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE)
    letter = models.CharField(max_length=1)
    players = models.ManyToManyField(Player, related_name='group_players')

    def __str__(self):
        return "{0} - Group {1}".format(self.tournament, self.letter)

    def get_table_data(self):
        data = []
        for player in self.players.all():
            matches = Match.objects.filter(models.Q(stage='Groups'),
                                           models.Q(tournament=self.tournament),
                                           models.Q(player1=player)|models.Q(player2=player),
                                           models.Q(finished=True))
            wins = matches.filter(winner=player).count()
            loses = matches.count() - wins
            result = '{0}-{1}'.format(wins, loses)
            games_won = 0
            games_lost = 0
            for match in matches:
                if match.player1 == player:
                    games_won += match.score1
                    games_lost += match.score2
                else:
                    games_won += match.score2
                    games_lost += match.score1                 
            record = '{0}-{1}'.format(games_won, games_lost)
            row_dict = {'player': player.name, 'record': record, 'result': result}
            data.append(row_dict)
        data = sorted(data, key=lambda k: int(k['result'][0])-int(k['result'][2]), reverse=True)
        return data

class Card(models.Model):

    cardID = models.CharField(max_length=10, default='AAA_000')
    name = models.CharField(max_length=30)
    text = models.TextField(null=True, blank=True)
    flavortext = models.TextField(null=True, blank=True)
    cost = models.PositiveSmallIntegerField()
    card_set = models.CharField(max_length=30, null=True, blank=True)
    CLASS = models.CharField(max_length=30, null=True, blank=True)
    cardtype = models.CharField(max_length=30, null=True, blank=True)
    attack = models.PositiveSmallIntegerField(null=True, blank=True)
    health = models.PositiveSmallIntegerField(null=True, blank=True)
    rarity = models.CharField(max_length=30)
    artist = models.CharField(max_length=30, null=True, blank=True)
    collectible = models.BooleanField(default=True, blank=True)
    image = models.ImageField(upload_to='hsapp/cards', null=True, blank=True)

    def __str__(self):
        return self.name



class Deck(models.Model):
    CLASSES = (
    ('MAGE', 'Mage'),
    ('WARRIOR', 'Warrior'),
    ('WARLOCK', 'Warlock'),
    ('HUNTER', 'Hunter'),
    ('PRIEST', 'Priest'),
    ('DRUID', 'Druid'),
    ('ROGUE', 'Rogue'),
    ('PALADIN', 'Paladin'),
    ('SHAMAN', 'Shaman'))

    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, null=True, blank=True, on_delete=models.CASCADE)
    deck_class = models.CharField(max_length=50, choices=CLASSES, null=True, blank=True)
    archetype = models.CharField(max_length=50, null=True, blank=True)
    cards = models.ManyToManyField(Card, blank=True)
    image = models.ImageField(upload_to='hsapp/decks/', null=True, blank=True)

    def __str__(self):
        deck_title = "{0} {1} - {2}".format(self.player, self.tournament, self.deck_class)
        return deck_title


class Deckset(models.Model):

    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.CASCADE)
    decks = models.ManyToManyField(Deck)

class Post(models.Model):

    title = models.CharField(max_length=300)
    article = models.TextField()
    tags = models.CharField(max_length=500, blank=True, null=True)
    #image = models.ImageField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    tournament = models.ForeignKey(Tournament, null=True, blank=True, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)

    def __str__(self):
        return self.title


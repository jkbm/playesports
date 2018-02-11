# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse 
from django_countries.fields import CountryField
from django.utils import timezone
# Create your models here.

class Team(models.Model):
    """CS GO team model"""
    name = models.CharField(max_length=200, unique=True)
    country = CountryField(null=True, blank=True)
    logo = models.ImageField(upload_to='csapp/teams',
                             null=True, blank=True)

    def __str__(self):
        return self.name

 
class Player(models.Model):
    """Class for competitive CS GO players"""
    name = models.CharField(max_length=200, unique=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    country = CountryField(null=True, blank=True)
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
    formerteams = models.ManyToManyField(Team, related_name='fteams')
    image = models.ImageField(upload_to='csapp/layers',
                              null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=False)
    current_squad = models.BooleanField(default=True)

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
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, related_name='teams')
    presenters = models.ManyToManyField(Player, related_name='presenters')
    groups = models.BooleanField(default=False)
    about = models.TextField(null=True, blank=True)
    format = models.TextField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    image = models.ImageField(upload_to='csapp/tournaments', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_location(self):
        """Format location to display"""
        location = "{0}, {1}".format(self.city, self.country.name)
        return location

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
    team1 = models.ForeignKey(Team, related_name='t1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='t2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Team, related_name='win', null=True, blank=True, on_delete=models.CASCADE)
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
            self.winner = self.team1
        elif int(self.score1) < int(self.score2):
            self.winner = self.team2
        super(Match, self).save(*args, **kwargs)

    def __str__(self):
        if self.finished is True:
            matchtitle = "{0}: {1} {2} {3}".format(self.tournament.title,
                                                   self.team1, self.score, self.team2)
        else:
            if self.team1.name != "None" or self.team2.name != "None":
                matchtitle = "{0}: {1} - {2}".format(self.tournament.title,
                                                     self.team1, self.team2)
            else:
                matchtitle = "{0}: {1}".format(self.tournament.title, self.stage)

        return matchtitle

    def short_title(self):
        if self.finished == True:
            matchtitle = "{0} {1} {2}".format(self.team1, self.score, self.team2)
        else:
            if self.team1.name != "None" or self.team2.name != "None":
                matchtitle = "{0} - {1}".format(self.team1, self.team2)
            else:
                matchtitle = "{0}".format( self.stage)
            

        return matchtitle

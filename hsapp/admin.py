# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Tournament, Player, Match, Game, Group, Card, Deck, Deckset, Post

admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Game)
admin.site.register(Group)
admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(Deckset)
admin.site.register(Post)

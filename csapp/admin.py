# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Tournament, Player, Match, Team, Post

admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Team)
admin.site.register(Post)
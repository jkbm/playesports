import requests
import urllib.request
from datetime import datetime
import time
from bs4 import BeautifulSoup
from .models import Match, Tournament, Player, Game, Group, Deck, Deckset
from django.db.models import Q
from django.core.files import File 
import json
import re
from xml.etree import ElementTree
def fill_from_text(tpk):

    t = Tournament.objects.get(pk=tpk)
    players = ['Chakki', 'Nostam', 'Talion', 'AlSkyHigh', 'chessdude123', 'Snail', 'wtybill']
    casters = []
    for p in players:
        obj, created = Player.objects.get_or_create(name=p)
        t.players.add(obj)
    t.save()

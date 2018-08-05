import requests
import urllib.request
from datetime import datetime
import time
from bs4 import BeautifulSoup
from .models import Match, Tournament, Player, Game, Group, Deck, Deckset, Card
#from django.db.models import Q
#from django.core.files import File 
import json
import re
from xml.etree import ElementTree
import os
import urllib.request

def import_cards():
    path = os.path.dirname(os.path.abspath(__file__)) + "/files/"
    abspath = os.path.dirname(os.path.abspath(__file__))
    filename = "witch2.json"
    with open(path+filename, 'r') as f:
        cards_j = json.loads(f.read())
        f.close()

    coll_cards_j = [x for x in cards_j if "collectible" in x]
    
    for card in coll_cards_j:
        if 'text' not in card:
            card['text'] = ""
        try:
            cargs = {'name':card['name'], 'text':card['text'], 'cost':card['cost'],
                                    'CLASS':card['playerClass'], 'rarity':card['rarity'], 'cardtype':card['type'],
                                    'card_set':card['cardSet'], 'image':'cards\{0}'.format(card['img'].split('/')[-1]),
                                    'flavortext':card['flavor'], 'artist':card['artist'], 'cardID':card['cardId']}
            #urllib.request.urlretrieve(card['img'], path+card['img'].split('/')[-1])
        except:
            print(card)
        Card.objects.create(**cargs)
    print(len(coll_cards_j))

if __name__ == "__main__":
    import_cards()
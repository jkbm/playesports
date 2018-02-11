from .models import Match, Player, Card
from django.db.models import Q
import sys
import xml.etree.ElementTree

RARITY = { '1': 'Basic', '2': 'Common', '3': 'Rare', '4': 'Epic', '5': 'Legendary'}
CARDTYPE = {'3': 'Hero', '4': 'Minion', '5': 'Spell', '6': 'Enchantment', '7': 'Weapon', '10': 'Hero power'}
CLASSES = {'1': 'Other', '12': 'Neutral', '10': 'Warrior', '11': 'Dream card',
           '2': 'Druid', '3': 'Hunter', '4': 'Mage', '5': 'Paladin', 
           '6': 'Priest', '7': 'Rogue', '8': 'Shaman', '9': 'Warlock'}
CARD_SETS = {'2': 'Basic', '3': 'Expert', '4': 'Hall of Fame', '5': 'Classic', '12': 'Naxxramas', '13': 'Goblins vs Gnomes', '14': 'Blackrock Mountain', '15': 'The Grand Tournament',
             '16': 'League of Explorers', '17': 'Heroes', '18': "Powers", '20': 'League OF Explorers', '21': 'Whispers of the Old Gods', '23': 'One Night in Karazhan',
             '24': 'One Night in Karazhan', '25': 'Mean Streets of Gadgetzan', '27': "Journey to Un'Goro", '1001': 'Knights of the Frozen Throne', }
def get_top(players):
    data = []
    for player in players:
        matches = Match.objects.filter( Q(player1=player) | Q(player2=player))
        wins = len(matches.filter(winner=player))
        loses = len(matches) - wins
        data.append({'player': player, 'wins': wins, 'loses': loses})
    data = sorted(data, key=lambda k: int(k['wins']) - int(k['loses']), reverse=True)
    return data[:10]

def get_cards():
    e = xml.etree.ElementTree.parse('F:\HereICode\esports\hsapp\static\hsdata\CardDefs.xml').getroot()
    return e

def get_classes(cards):
    sets = []
    for card in cards:
        for tag in card:
            if tag.get('name')=='CLASS':
                x = tag.get('value')
                if x not in sets:
                    sets.append(x)
    
    return sets

def get_names(cards, x):
    i = 0
    card_data = []
    for card in cards[:x]:
        name = "NONAME"
        cardtext = "NOINFO"
        flavortext = "NOINFO"
        cost = 0
        card_set = "NOINFO"
        CLASS = "NOINFO"
        cardtype = "NOINFO"
        card_set = ""
        image = card.get('CardID')
        artist = " "
        collectible = False
        for tag in card:
            if tag.get('name') == "CARDNAME":
                name = tag.find('enUS').text
            elif tag.get('name') == "CARDTEXT_INHAND":
                cardtext = tag.find('enUS').text
            elif tag.get('name') == "COST":
                cost = tag.get('value')
            elif tag.get('name') == "CLASS":
                CLASS = CLASSES[tag.get('value')]
            elif tag.get('name') == "RARITY":
                rarity = RARITY[tag.get('value')]
            elif tag.get('name') == "CARDTYPE":
               cardtype = CARDTYPE[tag.get('value')]
            elif tag.get('name') == "CARD_SET":
               card_set = CARD_SETS[tag.get('value')]
            elif tag.get('name') == "FLAVORTEXT":
                flavortext = tag.find('enUS').text
            elif tag.get('name') == "ARTISTNAME":
                artist = tag.text
            elif tag.get('name') == "COLLECTIBLE":
                collectible = True
        card_data.append([name, cardtext, cost, CLASS, rarity, cardtype, card_set, image, flavortext, artist, collectible])
    return card_data

def add_cards(data):
    x = 0
    for card in data:
        if card[10] == True:
            x+=1
    y = 0
    for card in data:
        if card[10] == True:
            y += 1
            Card.objects.create(name=card[0], text=card[1], cost=card[2],
                                CLASS=card[3], rarity=card[4], cardtype=card[5],
                                card_set=card[6], image='cards\{0}.png'.format(card[7]),
                                flavortext=card[8], artist=card[9], cardID=card[7])


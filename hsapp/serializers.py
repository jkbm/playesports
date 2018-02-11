from rest_framework import serializers
from .models import Player, Tournament, Match

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('name', 'country')

class TournamentSerializer(serializers.ModelSerializer):
    winner = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='hs:player_detail'
    )
    players = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name')

    class Meta:
        model = Tournament
        fields = ('title', 'start_date', 'end_date', 'winner',
                  'players', 'groups', 'format', 'image')

class MatchSerializer(serializers.ModelSerializer):

    player1 = serializers.SlugRelatedField(read_only=True, slug_field='name')
    player2 = serializers.SlugRelatedField(read_only=True, slug_field='name')
    winner = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Match
        fields = ('date', 'time', 'stage', 'format',
                  'player1', 'player2', 'winner', 'score')
                  
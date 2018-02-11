from django import forms
from django.core.validators import EmailValidator
from django.db.models import Q
from .models import Game, Match, Tournament, Group, Player, Post


class MatchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament')
        super(MatchForm, self).__init__(*args, **kwargs)
        try:
            self.fields['player1'].queryset = tournament.players.all()
            self.fields['player2'].queryset = tournament.players.all()
        except:
            self.fields['player1'].queryset = Player.objects.all()
            self.fields['player2'].queryset = Player.objects.all()
    class Meta:
        model = Match
        fields = ('tournament', 'date', 'player1', 'player2',
                  'score', 'format', 'stage', 'finished')

class GameForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match')
        super(GameForm, self).__init__(*args, **kwargs)
        try:
            self.initial['player1'] = Player.objects.get(pk=match.player1.pk)
            self.initial['player2'] = Player.objects.get(pk=match.player2.pk)
            self.fields['winner'].queryset = Player.objects.filter(
                pk__in=(match.player1.pk, match.player2.pk))
        except:
            self.fields['player1'].queryset = Player.objects.all()
            self.fields['player2'].queryset = Player.objects.all()

    class Meta:
        model = Game
        fields = ('match', 'player1', 'player2', 'class1', 'class2', 'winner')

class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        exclude = ['pk']

class TournamentForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = ('title', 'start_date', 'end_date', 'winner', 'players', 'groups')


class GroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament')
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['players'].queryset = tournament.players.all()

    class Meta:
        model = Group
        fields = ('tournament', 'letter', 'players')


class ControlPanelForm(forms.Form):

    tournament = forms.ModelChoiceField(queryset=Tournament.objects.all())

class FeedbackForm(forms.Form):

    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    feedback = forms.CharField(widget=forms.Textarea)

class AddPostForm(forms.Form):

    title = forms.CharField()
    tags = forms.CharField()
    article = forms.CharField(widget=forms.Textarea)
    
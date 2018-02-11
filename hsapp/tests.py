# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .models import Player
from django.utils import timezone
from django.core.urlresolvers import reverse

# Create your tests here.
class HsappTest(TestCase):

    def create_player(self, name = "Jack", birthday='1994-04-19', country='UA', team='CFC'):
        return Player.objects.create(name=name, birthday=birthday, country=country, team=team)

    def test_player_creation(self):
        w = self.create_player()
        self.assertTrue(isinstance(w, Player))
        self.assertEqual(w.__str__(), w.name)

    def test_hsapp_index_view(self):
        w = self.create_player()
        url = reverse("hsapp.views.tournament_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(w.title, resp.content)

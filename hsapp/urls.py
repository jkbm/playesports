# hsapp/urls.py
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "hsapp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tournament_list/$', views.tournament_list, name='tournament_list'),
    url(r'^control_panel/$', views.control_panel, name='control_panel'),
    url(r'^tournament/(?P<pk>\d+)/$', views.tournament_detail, name='tournament_detail'),
    url(r'^tournament/add/$', views.tournament_add, name='tournament_add'),
    url(r'^tournament/(?P<pk>\d+)/edit/$', views.tournament_edit, name='tournament_edit'),
    url(r'^tournament/(?P<pk>\d+)/unfinished/$', views.tournament_unfinished, name='tournament_unfinished'),
    url(r'^tournament/(?P<pk>\d+)/bracket/$', views.tournament_bracket, name='tournament_bracket'),
    url(r'^tournament/(?P<pk>\d+)/groups/add/$', views.group_add, name='group_add'),
    url(r'^player/(?P<pk>\d+)/$', views.player_detail, name='player_detail'),
    url(r'^player/add/$', views.player_add, name='player_add'),
    url(r'^players/$', views.players_list, name='players_list'),
    url(r'^match/(?P<pk>\d+)/$', views.match_detail, name='match_detail'),
    url(r'^like_match/$', views.like_match, name='like_match'),
    url(r'^matches/(?P<pk>\d+)/(?P<group>\w+)/$', views.match_list, name='match_list'),
    url(r'^match/add/(?P<pk>\d+)/$', views.match_add, name='match_add'),
    url(r'^match/add/$', views.match_add, name='match_add'),
    url(r'^game/add/(?P<match>\d+)/$', views.game_add, name='game_add'),
    url(r'^game/add/$', views.game_add, name='game_add'),
    url(r'^cards/(?P<card_set>\d+)/$', views.cards, name='cards'),
    url(r'^cards/$', views.cards, name='cards'),    
    url(r'^search$', views.search, name="search"),
    url(r'^about/$', views.about, name='about'),
    url(r'^feedback/$', views.FeedbackView.as_view(), name='feedback'),
    url(r'^new-article/$', views.AddPost.as_view(), name='post_add'),
    url(r'^articles/$', views.post_list, name='post_list'),
    url(r'^articles/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^articles/(?P<pk>\d+)/edit/$', views.EditPost.as_view(), name='post_edit'),
    url(r'^articles/(?P<tag>[\w\ ]+)/$', views.post_list, name='post_list'),
    url(r'^api/player/$', views.PlayerCreateReadView.as_view(), name='player_rest_api'),
    url(r'^api/player/(?P<name>\w+)/$', views.PlayerReadUpdateDeleteView.as_view(), name='player_rest_api'),
    url(r'^api/tournament/$', views.TournamentCreateReadView.as_view(), name='tournament_rest_api'),
    url(r'^api/tournament/(?P<pk>\d+)/$', views.TournamentReadUpdateDeleteView.as_view(), name='tournament_rest_api'),
    url(r'^api/match/$', views.MatchCreateReadView.as_view(), name='match_rest_api'),
    url(r'^api/match/(?P<pk>\d+)/$', views.MatchReadUpdateDeleteView.as_view(), name='match_rest_api'),
    url(r'^temp/$', views.temp, name='temp')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

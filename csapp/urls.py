# blog/urls.py
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'csapp'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^teams/$', views.teams_list, name="teams_list"),
    url(r"^teams/(?P<pk>\d+)/$", views.team_detail, name='team_detail'),
    url(r"^tournaments/$", views.tournament_list, name="tournament_list"),
    url(r"^tournaments/(?P<pk>\d+)/$", views.tournament_detail, name='tournament_detail'),
    url(r"^players/$", views.player_list, name='player_list'),
    url(r"^players/(?P<pk>\d+)/$", views.player_detail, name='player_detail'),
    url(r'^search$', views.search, name="search"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

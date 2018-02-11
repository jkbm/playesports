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
    url(r'^search$', views.search, name="search"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

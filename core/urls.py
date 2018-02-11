# blog/urls.py
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax$', views.ajax, name='ajax'),
    url(r'^ajax2$', views.ajax2, name='ajax2'),
    url(r'^nopage$', views.nopage, name='nopage'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

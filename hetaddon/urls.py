from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^api/projects$', views.projects, name='projects'),
    url(r'^api/projects/(?P<id>[0-9]+)/documents$', views.projectDocuments, name='projectDocuments'),
    url(r'^api/projects/(?P<id>[0-9]+)/requirements$', views.projectRequirements, name='projectRequirements')
]
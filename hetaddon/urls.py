from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^api/projects$', views.project_handler, name='projects'),
    url(r'^api/projects/(?P<id>[0-9]+)$', views.project_handler, name='project'),
    url(r'^api/folders$', views.folder_handler, name='folders'),
    url(r'^api/folders/(?P<id>[0-9]+)$', views.folder_handler, name='folders'),
    url(r'^api/documents$', views.document_handler, name='documents'),
    url(r'^api/documents/(?P<id>[0-9]+)$', views.document_handler, name='documents'),
    url(r'^api/projects/(?P<id>[0-9]+)/documents$', views.get_documents_of_project_json, name='projectDocuments'),
    url(r'^api/projects/(?P<id>[0-9]+)/requirements$', views.get_requirements_of_project_json, name='projectRequirements')
]
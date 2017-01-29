from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^api/projects$', views.get_projects_json, name='projects'),
    url(r'^api/folders$', views.get_folders_json, name='folders'),
    url(r'^api/folderStructure$', views.get_folderstructure_json, name='folders'),
    url(r'^api/folderStructureOfProject/(?P<id>[0-9]+)$', views.get_folderstructure_json, name='folders'),
    url(r'^api/projects/(?P<id>[0-9]+)/documents$', views.get_documents_of_project_json, name='projectDocuments'),
    url(r'^api/projects/(?P<id>[0-9]+)/requirements$', views.get_requirements_of_project_json, name='projectRequirements')
]
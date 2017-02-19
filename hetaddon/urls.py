from django.conf.urls import url

from hetaddon.views import views
from hetaddon.auth import authView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^api/auth/installed', authView.addon_installed, name='addonInstalled'),
    url(r'^api/projects$', views.project_handler, name='projects'),
    url(r'^api/projects/(?P<id>[0-9]+)$', views.project_handler, name='project'),
    url(r'^api/folders$', views.folder_handler, name='folders'),
    url(r'^api/folders/(?P<id>[0-9]+)$', views.folder_handler, name='folders'),
    url(r'^api/documents$', views.document_handler, name='documents'),
    url(r'^api/documents/(?P<id>[0-9]+)$', views.document_handler, name='documents'),
    url(r'^api/requirements$', views.requirement_handler, name='requirements'),
    url(r'^api/requirements/(?P<id>[0-9]+)$', views.requirement_handler, name='requirements'),
    url(r'^api/values/(?P<id>[0-9]+)$', views.requirement_value_handler, name='requirementValues'),
    url(r'^api/projects/(?P<id>[0-9]+)/documents$', views.get_documents_of_project_json, name='projectDocuments'),
    url(r'^api/projects/(?P<id>[0-9]+)/requirements$', views.get_requirements_of_project_json, name='projectRequirements')
]
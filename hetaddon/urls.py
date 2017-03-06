from django.conf.urls import url

from hetaddon.views.views_handler import *
from hetaddon.auth import auth_views

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^index$', index, name='index'),
    url(r'^api/auth/installed', auth_views.addon_installed, name='addonInstalled'),
    url(r'^api/projects$', project_handler, name='projects'),
    url(r'^api/projects/(?P<id>[0-9]+)$', project_handler, name='project'),
    url(r'^api/folders$', folder_handler, name='folders'),
    url(r'^api/folders/(?P<id>[0-9]+)$', folder_handler, name='folders'),
    url(r'^api/documents$', document_handler, name='documents'),
    url(r'^api/documents/(?P<id>[0-9]+)$', document_handler, name='documents'),
    url(r'^api/requirements$', requirement_handler, name='requirements'),
    url(r'^api/requirements/(?P<id>[0-9]+)$', requirement_handler, name='requirements'),
    url(r'^api/values/(?P<id>[0-9]+)$', requirement_value_handler, name='requirementValues'),
    url(r'^api/sections$', section_handler, name='sections'),
    url(r'^api/sections/(?P<id>[0-9]+)$', section_handler, name='sections'),
    url(r'^api/projects/(?P<id>[0-9]+)/sections$', get_sections_of_project_json, name='projectSections'),
    url(r'^api/projects/(?P<id>[0-9]+)/requirements$', get_requirements_of_project_json, name='projectRequirements'),
    url(r'^api/projects/(?P<id>[0-9]+)/analyze$', analyze_project, name='analyzeProject')
]
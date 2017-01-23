from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Project)
admin.site.register(Folder)
admin.site.register(Document)
admin.site.register(Requirement)
admin.site.register(User)
admin.site.register(Section)
admin.site.register(DocumentCategory)
admin.site.register(Membership)
admin.site.register(ExternalPlatform)
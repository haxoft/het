from django.db import models


class User(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128)

    def __str__(self):
        return "{ name:" + self.name + ", email:" + self.email + "}"


class ExternalPlatform(models.Model):
    PLATFORMS = (
        ('atl', 'Atlassian'),
        ('fac', 'Facebook'),
        ('goo', 'Google')
    )
    platform_name = models.CharField(max_length=3, choices=PLATFORMS)
    user_ext_id = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{ name:" + self.platform_name + ", userExtId:" + str(self.user_ext_id) + ", userId:" + str(self.user.id) + " }"


class Folder(models.Model):
    name = models.CharField(max_length=128)
    parent_folder = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    projects = models.ManyToManyField('Project', through='ProjectFolder')

    def __str__(self):
        return "{ id:" + str(self.id) + ", name:" + str(self.name) + ", parentFolder:" + str(self.parent_folder.id if self.parent_folder is not None else "None") + " }"


class RootFolder(Folder):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{ id:" + str(self.id) + ", name:" + str(self.name) + ", owner:" + str(self.owner.id) + "}"


class Project(models.Model):
    name = models.CharField(max_length=128)
    created = models.DateTimeField()
    members = models.ManyToManyField(User, through='Membership')

    def __str__(self):
        return "{ name:" + self.name + ", # of members:" + str(len(list(self.members.all()))) + " }"


class ProjectFolder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    def __str__(self):
        return "{ project:" + str(self.project_id) + ", folder:" + str(self.folder_id) + " }"


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #  some other fields might be added, e.g. role, date, etc.


class Section(models.Model):
    name = models.CharField(max_length=128)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)


class Document(models.Model):
    CATEGORIES = (
        ('cal', 'Call for Proposal'),
        ('rul', 'Rules/Limitations'),
        ('tem', 'Template'),
        ('oth', 'Other')
    )
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    size = models.IntegerField(default=0)
    status = models.CharField(max_length=128)
    category = models.CharField(max_length=3, choices=CATEGORIES)
    content = models.BinaryField(null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return "{ name:" + self.name + ", type:" + self.type + ", size:" + str(self.size) + ", status:" + self.status \
               + ", category:" + self.category + ", section:" + str(self.section_id) + " }"


class Requirement(models.Model):
    name = models.CharField(max_length=128)
    values_shown = models.IntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class RequirementValue(models.Model):
    value = models.TextField()
    disabled = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    rating = models.FloatField()
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    # don't delete the value when the doc is removed
    document = models.ForeignKey(Document, null=True, on_delete=models.SET_NULL)


class TenantInfo(models.Model):
    key = models.CharField(max_length=128)
    client_key = models.CharField(max_length=128, unique=True)
    shared_secret = models.CharField(max_length=128)





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

    def __str__(self):
        parent_folder = ", parentFolder:" + ("NULL" if (self.parent_folder is None) else str(self.parent_folder.id))
        return "{ name:" + self.name + parent_folder + " }"


class Section(models.Model):
    name = models.CharField(max_length=128)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)


class Project(models.Model):
    name = models.CharField(max_length=128)
    created = models.DateTimeField()
    members = models.ManyToManyField(User, through='Membership')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    def __str__(self):
        return "{ name:" + self.name + ", folder:" + str(self.folder.id) + " }"


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #  some other fields might be added, e.g. role, date, etc.


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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class RequirementValue(models.Model):
    value = models.CharField(max_length=300)
    disabled = models.BooleanField(default=False)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    # don't delete the value when the doc is removed
    document = models.ForeignKey(Document, null=True, on_delete=models.SET_NULL)





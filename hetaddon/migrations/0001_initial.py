# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 17:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=128)),
                ('size', models.IntegerField(default=0)),
                ('status', models.CharField(max_length=128)),
                ('category', models.CharField(choices=[('cal', 'Call for Proposal'), ('rul', 'Rules/Limitations'), ('tem', 'Template'), ('oth', 'Other')], max_length=3)),
                ('content', models.BinaryField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalPlatform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(choices=[('atl', 'Atlassian'), ('fac', 'Facebook'), ('goo', 'Google')], max_length=3)),
                ('user_ext_id', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('created', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFolder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Requirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('values_shown', models.IntegerField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Project')),
            ],
        ),
        migrations.CreateModel(
            name='RequirementValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=300)),
                ('disabled', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
                ('rating', models.FloatField()),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hetaddon.Document')),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Requirement')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Project')),
            ],
        ),
        migrations.CreateModel(
            name='TenantInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128)),
                ('client_key', models.CharField(max_length=128, unique=True)),
                ('shared_secret', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='RootFolder',
            fields=[
                ('folder_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hetaddon.Folder')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.User')),
            ],
            bases=('hetaddon.folder',),
        ),
        migrations.AddField(
            model_name='projectfolder',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Folder'),
        ),
        migrations.AddField(
            model_name='projectfolder',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Project'),
        ),
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(through='hetaddon.Membership', to='hetaddon.User'),
        ),
        migrations.AddField(
            model_name='membership',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Project'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.User'),
        ),
        migrations.AddField(
            model_name='folder',
            name='parent_folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Folder'),
        ),
        migrations.AddField(
            model_name='folder',
            name='projects',
            field=models.ManyToManyField(through='hetaddon.ProjectFolder', to='hetaddon.Project'),
        ),
        migrations.AddField(
            model_name='externalplatform',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.User'),
        ),
        migrations.AddField(
            model_name='document',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hetaddon.Section'),
        ),
    ]

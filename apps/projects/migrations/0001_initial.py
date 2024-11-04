# Generated by Django 5.1 on 2024-11-03 15:30

import autoslug.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, max_length=50, verbose_name='Name')),
            ],
            options={
                'ordering': ['-created'],
                'indexes': [models.Index(fields=['name'], name='projects_ta_name_536b15_idx')],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='title', unique=True)),
                ('featured_image', models.ImageField(blank=True, upload_to='featured_image/', verbose_name='Featured Image')),
                ('description', models.TextField(verbose_name='Description')),
                ('source_link', models.CharField(blank=True, max_length=200, verbose_name='Source Code Link')),
                ('demo_link', models.CharField(blank=True, max_length=200, verbose_name='Demo Link')),
                ('vote_total', models.IntegerField(default=0, verbose_name='Vote Total')),
                ('vote_ratio', models.IntegerField(default=0, verbose_name='Vote Ratio')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='profiles.profile')),
                ('tags', models.ManyToManyField(to='projects.tag')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('value', models.CharField(choices=[('up', 'Up Vote'), ('down', 'Down Vote')], max_length=4)),
                ('content', models.TextField(verbose_name='Content')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='projects.project')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='profiles.profile')),
            ],
            options={
                'ordering': ['-created'],
                'unique_together': {('project', 'reviewer')},
            },
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['-created'], name='projects_pr_created_5ace3f_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['title', 'description'], name='projects_pr_title_4ec0e6_idx'),
        ),
    ]

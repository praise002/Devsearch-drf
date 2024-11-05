# Generated by Django 5.1 on 2024-11-05 16:27

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
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Name')),
                ('email', models.EmailField(max_length=200, verbose_name='Email')),
                ('subject', models.CharField(max_length=200, verbose_name='Subject')),
                ('body', models.TextField(verbose_name='Body')),
                ('is_read', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to='profiles.profile')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.profile')),
            ],
            options={
                'ordering': ['is_read', '-created'],
                'indexes': [models.Index(fields=['created'], name='messaging_m_created_aa21b6_idx')],
            },
        ),
    ]

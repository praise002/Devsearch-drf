# Generated by Django 5.1 on 2025-04-22 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
    ]

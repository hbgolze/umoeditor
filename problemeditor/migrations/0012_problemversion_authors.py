# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-01 22:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problemeditor', '0011_problemversion_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemversion',
            name='authors',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]

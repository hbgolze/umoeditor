# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-12 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problemeditor', '0007_finaltest'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='author_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]

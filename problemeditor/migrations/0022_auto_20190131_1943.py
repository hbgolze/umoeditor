# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2019-02-01 02:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problemeditor', '0021_auto_20190131_1942'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statustopic',
            options={'ordering': ['order', 'topic']},
        ),
    ]

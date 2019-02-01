# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2019-02-01 02:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problemeditor', '0018_shortlist_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemstatus',
            name='approval_user',
        ),
        migrations.RemoveField(
            model_name='problemstatus',
            name='author_name',
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_status_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='problemeditor.ProblemStatus'),
        ),
        migrations.AddField(
            model_name='problem',
            name='topic_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='problemeditor.Topic'),
        ),
        migrations.AddField(
            model_name='problemstatus',
            name='description',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='topic',
            name='short_topic',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='problemstatus',
            name='status',
            field=models.CharField(blank=True, max_length=2),
        ),
    ]
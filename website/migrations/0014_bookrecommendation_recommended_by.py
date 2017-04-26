# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-19 08:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0013_auto_20170419_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookrecommendation',
            name='recommended_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
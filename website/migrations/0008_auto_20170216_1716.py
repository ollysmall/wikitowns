# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-16 17:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20170216_1638'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='websiterecommendation',
            unique_together=set([('category', 'subcategory', 'url')]),
        ),
    ]

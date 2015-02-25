# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('xblog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='guid',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pingback',
            name='mod_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 54, 24, 529508), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pingback',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 54, 24, 529481), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 54, 24, 531470), blank=True),
            preserve_default=True,
        ),
    ]

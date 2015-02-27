# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('xblog', '0002_auto_20150225_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pingback',
            name='mod_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 27, 9, 49, 57, 800478), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pingback',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 27, 9, 49, 57, 800448), blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 27, 9, 49, 57, 802400), blank=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.manager
import django.utils.timezone
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('xblog', '0003_auto_20150227_0949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='blog',
        ),
        migrations.AlterModelManagers(
            name='blog',
            managers=[
                (b'objects', django.db.models.manager.Manager()),
                (b'on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='post',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='post',
            name='primary_category_name',
        ),
        migrations.AddField(
            model_name='post',
            name='post_format',
            field=models.CharField(default=b'standard', max_length=100, blank=True, choices=[(b'standard', b'Standard'), (b'video', b'Video'), (b'status', b'Status')]),
        ),
        migrations.AlterField(
            model_name='pingback',
            name='author_email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='pingback',
            name='mod_date',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='pingback',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(to='xblog.Author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='xblog.Tag', blank=True),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fullname', models.CharField(max_length=100, blank=True)),
                ('url', models.URLField(blank=True)),
                ('avatar', models.ImageField(height_field=b'avatar_height', width_field=b'avatar_width', upload_to=b'avatars', blank=True)),
                ('about', models.TextField(blank=True)),
                ('avatar_height', models.IntegerField(null=True, blank=True)),
                ('avatar_width', models.IntegerField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField(blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('blog', models.ForeignKey(to='xblog.Blog')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(blank=True)),
                ('link_name', models.CharField(max_length=255, blank=True)),
                ('link_image', models.ImageField(height_field=b'link_image_height', width_field=b'link_image_width', upload_to=b'blog_uploads/links/', blank=True)),
                ('link_image_height', models.IntegerField(null=True, blank=True)),
                ('link_image_width', models.IntegerField(null=True, blank=True)),
                ('description', models.TextField(blank=True)),
                ('visible', models.BooleanField(default=True)),
                ('rss', models.URLField(blank=True)),
                ('blog', models.ForeignKey(to='xblog.Blog')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LinkCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('visible', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(null=True, blank=True)),
                ('blog', models.ForeignKey(to='xblog.Blog')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pingback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(max_length=100, blank=True)),
                ('author_email', models.EmailField(max_length=75, blank=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('body', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('source_url', models.URLField(blank=True)),
                ('target_url', models.URLField(blank=True)),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 53, 53, 636733), blank=True)),
                ('mod_date', models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 53, 53, 636762), blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2015, 2, 25, 9, 53, 53, 639066), blank=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('enable_comments', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=100)),
                ('body', models.TextField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('status', models.CharField(default=b'Draft', max_length=32, null=True, blank=True, choices=[(b'draft', b'Draft'), (b'publish', b'Published'), (b'private', b'Private')])),
                ('text_filter', models.CharField(default=b'__default__', max_length=100, blank=True, choices=[(b'markdown', b'Markdown'), (b'html', b'HTML'), (b'convert linebreaks', b'Convert linebreaks')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('blog', models.ForeignKey(to='xblog.Blog')),
                ('categories', models.ManyToManyField(to='xblog.Category')),
                ('primary_category_name', models.ForeignKey(related_name='primary_category_set', blank=True, to='xblog.Category', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='xblog.Tag', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pingback',
            name='post',
            field=models.ForeignKey(to='xblog.Post'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='category',
            field=models.ForeignKey(to='xblog.LinkCategory'),
            preserve_default=True,
        ),
    ]

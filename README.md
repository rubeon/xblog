XBlog
=====

This is a messy blogging system for Django.  It was originally designed to 
work tightly with a couple of related projects, XComments and XGallery.

It has some interesting features, including Blogging API support for:

- Metaweblog

- Wordpress

- MovableType

This project is intended to fix up that support, and modernize it for current
versions of Django.

Installation
------------

On Ubuntu 12.04, this is fairly easy to install. 

    $ sudo apt-get install python-django git python-markdown python-beautifulsoup
    $ mkdir -p ~/dev/x/
    $ cd ~/dev/x/
    $ django-admin startproject mysite
    $ cd mysite
    $ git clone https://github.com/rubeon/xblog.git
    
Create a file in the project directory (e.g., ~/dev/x/mysite) called 
`settings_local.py` with the following settings:

`
    DEBUG=True
    TEMPLATE_DEBUG=True
    SITE_URL = "http://youbitch.rupert.subcritical.org/"
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.flatpages',
        'django.contrib.markup',  
        'django.contrib.sessions',
        'django.contrib.sitemaps',
        'django.contrib.sites',
        'xblog',
        # 'common.xcomments',   
        # 'common.xgallery',
    )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', 
            'NAME': 'mysite.db',
        }
    }

    TIME_ZONE="Europe/London"
    ROOT_URLCONF='mysite.urls'    
`

Edit the urls.py so that /blog and /admin are defined:

    urlpatterns = patterns('',
        # Uncomment the next line to enable the admin:
        url(r'^admin/', include(admin.site.urls)),
        (r'^blog/',include('xblog.urls')),
     
    )

In the bottom of settings.py for your site, you can import this file's contents:

`from settings_local import *`

Setup the database:

    PYTHONPATH=$PWD:$PWD/.. python manage.py syncdb



Next, create a script to run the server in local mode for debugging:

    #!/bin/bash

    PYTHONPATH=$PWD:$PWD/.. python manage.py runserver 0.0.0.0:9111


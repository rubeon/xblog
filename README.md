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

    $ sudo apt-get install python-django git
    $ mkdir -p ~/dev/x/
    $ cd ~/dev/x/
    $ django-admin startproject mysite
    $ cd mysite
    $ git clone https://github.com/rubeon/xblog.git
    
Create a file in the project directory (e.g., ~/dev/x/mysite) called 
`settings_local.py` with the following settings:


`SITE_URL = "http://youbitch.org/"`

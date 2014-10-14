# encoding: utf-8
"""
urls.py

Created by Eric Williams on 2007-02-27.
"""

try:
    from django.conf.urls.defaults import *
except ImportError:
    # defaults no longer there...
    from django.conf.urls import patterns, include, url
    
from django.contrib.sitemaps import GenericSitemap
from django.views.generic import ListView, DetailView

from feeds import *
from models import Post
from views.sitemap import BlogSitemap

feeds = {
    'blogs': Posts,
    #'podcasts': Podcasts,
}

sitemaps = {
    'blog':BlogSitemap()
}
info_dict = {
    'queryset':Post.objects.all().filter(status='publish'),
    'date_field':'pub_date'
}


urlpatterns = patterns('',
    # Index, defaults to "post_list.html"
    url(r'^(?P<page>\d+)?/?$', 
        ListView.as_view(
            model=Post, 
            paginate_by=5, 
        ),
        name='index',
    ),

)



# urlpatterns = patterns(  '',
#     # (r'^gallery/$', 'blog.xmlrpc_views.call_xmlrpc', {'module':'gallery.galleryAPI'}),
#     (r'^xmlrpc/*','xblog.views.xmlrpc_views.call_xmlrpc', {'module':'xblog.metaWeblog'}),
#     (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
#     (r'^.*/(?P<slug>[-\w]+)/edit/$',   'xblog.views.edit.edit_post'),
#     (r'^.*/(?P<slug>[-\w]+)/trackback/$', 'xblog.ping_modes.process_trackback'),
#     ('^$', 'xblog.views.blog.blog_overview'),
#     # ('^archive/', include('blog.archive_urls')),
#     )
# urlpatterns += patterns(  'django.views.generic.date_based',
#     (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$',   'object_detail', dict(info_dict, slug_field='slug')),
#     (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',                    'archive_day',   dict(info_dict,month_format="%b")),
#     (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$',                                     'archive_month', info_dict),
#     (r'^(?P<year>\d{4})/$',                                                         'archive_year',  dict(info_dict, make_object_list=True)),
#     (r'^archives/$',                                                               'archive_index', dict(info_dict)),
#     # (r'^tag/(?P<tag>.*)/',                                                            'blog.views.tag_overview'),
# )
# 
# urlpatterns += patterns(  'django.contrib.sitemaps.views',
#     (r'^sitemap.xml$',      'index', {'sitemaps': sitemaps}),
#     (r'^sitemap-blog.xml$', 'sitemap', {'sitemaps': sitemaps}),
# )
# 
#!/usr/bin/env python
# encoding: utf-8
"""
metaWeblog.py

Created by Eric Williams on 2007-02-22.
"""
import string
import xmlrpclib
import urllib
import re
import time
import datetime
import os
import urlparse
import sys
from django.contrib.auth.models import User
# from django.contrib.comments.models import FreeComment
from django.conf import settings
from xblog.models import Tag, Post, Blog, Author, Category, FILTER_CHOICES
from views.xmlrpc_views import public
import BeautifulSoup
from ping_modes import send_pings

# import config
# import xmlrpclib.DateTime

# I guess it's time to fix that upload issue...
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import logging
logger = logging.getLogger(__name__)

def authenticated(pos=1):
    # tells the method that the visitor is authenticated
    logger.debug("authenticated entered")
    def _decorate(func):
        def _wrapper(*args, **kwargs):
            username = args[pos+0]
            password = args[pos+1]
            args = args[0:pos]+args[pos+2:]
            try:
                logger.info("Username: %s" % username)
                # print "Password: ", password
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                logger.debug("username %s, password %s, args %s" % (username, "password", args))
                logger.warn( "User.DoesNotExist")
                raise ValueError("Authentication Failure")
            if not user.check_password(password):
                logger.warn( "User.check_password")
                raise ValueError("Authentication Failure")
            if not user.is_superuser:
                logger.warn("user.is_superuser")
                raise ValueError("Authorization Failure")
            return func(user, *args, **kwargs)

        return _wrapper
    return _decorate

def full_url(url):
    return urlparse.urljoin(settings.SITE_URL, url)

@public
@authenticated()
def metaWeblog_getCategories(user, blogid, struct={}):
    """ 
    takes the blogid, and returns a list of categories
    struct:
    string categoryId
    string parentId
    string categoryName
    string categoryDescription
    string description: Name of the category, equivalent to categoryName.
    string htmlUrl
    string rssUrl
    
    
    """
    logger.debug("metaWeblog_getCategories called")
    categories = Category.objects.all()
    res=[]
    for c in categories:
        struct={}
        struct['categoryId'] = str(c.id)
        # struct['parentId'] = str(0)
        struct['categoryName']= c.title
        struct['parentId'] = ''
        struct['title'] = c.title
        # if c.description == '':
        #     struct['categoryDescription'] = c.title
        # else:
        #     struct['categoryDescription'] = c.description
        # struct['description'] = struct['categoryDescription']
        struct['htmlUrl'] = "http://dev.ehw.io"
        
        res.append(struct)
    logger.debug(res)
    return res

@public
@authenticated()
def metaWeblog_newMediaObject(user, blogid, struct):
    """ returns struct with url..."""
    logger.debug( "metaWeblog_newMediaObject called")
    upload_dir = "blog_uploads/%s" % urllib.quote(user.username)
    bits       = struct['bits']
    mime       = struct['type']
    name       = struct['name']    
    savename   = name
    logger.debug( "savename: %s" %  savename)
    save_path = os.path.join(upload_dir, savename)
    logger.debug("Saving to %s" % save_path)
    path = default_storage.save(save_path, ContentFile(bits))
    logger.debug("Path: %s" % path)
    res = {}
    res['url']= default_storage.url(path)
    logger.debug(res)
    return res


 
@public
@authenticated()
def metaWeblog_newPost(user, blogid, struct, publish="PUBLISH"):
    """ mt's newpost function..."""
    logger.debug( "metaWeblog.newPost called")
    logger.debug("user: %s" % user)
    logger.debug("blogid: %s" % blogid)
    logger.debug("struct: %s" % struct)
    logger.debug("publish: %s" % publish)
    body = struct['description']
    blog = Blog.objects.get(pk=blogid)
    pub_date = datetime.datetime.now()
    
    post = Post(
        title=struct['title'],
        body = body,
        create_date = pub_date,
        update_date = pub_date,
        pub_date = pub_date,
        status = publish and 'publish' or 'draft',
        blog = blog,
        author =user
    )
    post.prepopulate()
    logger.debug( "Saving")
    # need to save beffore setting many-to-many fields, silly django
    post.save()
    categories = struct.get("categories", [])
    logger.debug("Setting categories: %s" % categories)
    clist = []
    for category in categories:
        try:
            c = Category.objects.filter(blog=blog, title=category)[0]
            logger.debug("Got %s" % c)
            clist.append(c)
        except Exception, e:
            logger.warn(str(e))
    post.categories=clist
    post.save()
    logger.info("Post %s saved" % post)
    logger.info("Setting Tags")
    setTags(post, struct)
    logger.debug("Handling Pings")
    logger.info("sending pings to host")
    send_pings(post)
    logger.debug("newPost finished")
    return post.id
    
@public
@authenticated()
def metaWeblog_editPost(user, postid, struct, publish):
    logger.debug( "metaWeblog_editPost")
    post = Post.objects.get(id=postid)
    title = struct.get('title', None)
    if title is not None:
        post.title = title
    
    body           = struct.get('description', None)
    text_more      = struct.get('mt_text_more', '')
    allow_pings    = struct.get('mt_allow_pings',1)

    description    = struct.get('description','')
    keywords       = struct.get('mt_keywords',[])
    text_more      = struct.get('mt_text_more',None)
    
    if text_more:
      # has the extended entry stuff...
      body = string.join([body, text_more], "<!--more-->")
    
    post.enable_comments = bool(struct.get('mt_allow_comments',1)==1)
    post.text_filter    = struct.get('mt_convert_breaks','html').lower()
    
    if body is not None:
        post.body = body
        # todo - parse out technorati tags
    if user:
        post.author = user 
    
    if publish:
      post.status = "publish"
    else:
      post.status = "draft"
      
    setTags(post, struct)
    post.update_date = datetime.datetime.now()
    post.save()
    # FIXME: do I really want trackbacks?
    send_pings(post)
    return True

# def metaWeblog_editPost(user, postid, struct, publish):
#     """ edit an existing post..."""
#     print "metaWeblog.editPost called"
#     p = Post.objects.get(pk=postid)
#     print "Got post:", p
#     # update the settings...
#     title = struct.get('title',None)
#     if title is not None:
#         p.title = title
#     body = struct.get('description', None)
#     if body is not None:
#         p.body = body
# 
#     p.status = publish and 'Published' or 'Draft'
#     setTags(p, struct)
#     p.save()
#     print "P saved"
#     return True
# 
@public
@authenticated()
def metaWeblog_getPost(user, postid):
    """ returns an existing post """
    logger.debug( "metaWeblog.getPost called ")
    post = Post.objects.get(pk=postid)
    # post.create_date = format_date(datetime.datetime.now())
    return post_struct(post)

@public
@authenticated(pos=2)
def blogger_getRecentPosts(user, appkey, blogid, num_posts=50):
    """ returns a list of recent posts """
    logger.debug( "blogger.getRecentPosts called...")
    blog = Blog.objects.get(id=blogid)
    posts = blog.post_set.order_by('-pub_date')[:num_posts]
    return [post_struct(post) for post in posts]

@public
@authenticated()
def metaWeblog_getRecentPosts(user, blogid, num_posts=50):
    """ returns a list of recent posts..."""
    logger.debug( "metaWeblog.getRecentPosts called...")
    logger.debug( "user %s, blogid %s, num_posts %s" % (user, blogid, num_posts))
    logger.info("WordPress compatibility, ignoring blogid")
    # blog = Blog.objects.get(id=blogid)
    posts = user.post_set.order_by('-pub_date')[:num_posts]
    return [post_struct(post) for post in posts]
    

@public
@authenticated()
def blogger_getUserInfo(user, appkey):
    """ returns userinfo for particular user..."""
    logger.debug( "blogger.getUserInfo called")
    # author = user # Author.objects.get(user=user)
    firstname = user.first_name
    lastname = user.last_name
    struct = {}
    struct['username']=user.username
    struct['firstname']=firstname
    struct['lastname']=lastname
    struct['nickname']= user.author.fullname
    struct['url'] = user.author.url
    struct['email'] = user.email
    struct['userid'] = str(user.id)
    return struct

@public
@authenticated()
def blogger_getUsersBlogs(user, appkey):
    logger.debug( "blogger.getUsersBlogs called")
    # print "Got user", user
    usersblogs = Blog.objects.filter(owner=user)
    logger.debug( "%s blogs for %s" % (usersblogs, user))
    # return usersblogs
    res = [
    {
    'blogid':str(blog.id),
    'blogName': blog.title,
    'url': blog.get_url()
    } for blog in usersblogs
    ]
    logger.debug(res)
    return res

@public
@authenticated()
def metaWeblog_getUsersBlogs(user, appkey):
  # the original metaWeblog API didn't include this
  # it was added in 2003, once blogger jumped ship from using
  # the blogger API
  # http://www.xmlrpc.com/stories/storyReader$2460
  logger.debug( "metaWeblog.getUsersBlogs called")
  usersblogs = Blog.objects.filter(owner=user)
  logger.debug( "%s blogs for %s" % (usersblogs, user))
  # return usersblogs
  res = [
    {
      'blogid':str(blog.id),
      'blogName': blog.title,
      'url': blog.get_url()
    } for blog in usersblogs
    ]
  logger.debug(res)
  return res
  
@public
@authenticated()
def mt_publishPost(user, postid):
    """
    lies that it publishes the thing, mostly for compatibility
    porpoises...
    """
    return True
    
    
@public
@authenticated(pos=2)
def blogger_deletePost(user, appkey, post_id, publish):
    """ deletes the specified post..."""
    logger.debug("blogger.deletePost called")
    #print "GOT APPKEY", appkey
    #print "GOT PUBLISH:",publish
    post = Post.objects.get(pk=post_id)
    #print "DELETING:",post
    post.delete()
    
    return True
    
# metaWeblog_getCategories removed in deference to mt.getCategoryList
#@public
#@authenticated()
#def metaWeblog_getCategories(user, blogid):
#    """ returns a list of cateogires"""
#    print "metaWeblog_getCategories called"
#    categories = Category.objects.all()
#    res = []
#    for c in categories:
#        struct = {}
#        struct['description']=c.title
#        struct['htmlUrl']=''
#        struct['rssUrl']=''
#        res.append(struct)
#    
#    return res

# mt_getCategoryList=metaWeblog_getCategories

@public
@authenticated()
def mt_getCategoryList(user, blogid):
    """ takes the blogid, and returns a list of categories"""
    logger.debug( "mt_getCategoryList called")
    categories = Category.objects.all()
    res=[]
    for c in categories:
        struct={}
        struct['categoryId']= str(c.id)
        struct['categoryName']= c.title
        res.append(struct)
    return res
    

def post_struct(post):
    """ returns the meta-blah equiv of a post """
    logger.debug("post_struct called")
    # link = full_url(post.get_absolute_url())
    link = post.get_absolute_url()
    categories = post.categories.all()
    # check to see if there's a more tag...
    if post.body.find('<!--more-->') > -1:
      description, mt_text_more = post.body.split('<!--more-->')
    else:
      description = post.body
      mt_text_more = ""
    
    if post.enable_comments:
      mt_allow_comments = 1
    else:
      mt_allow_comments = 2
    
    struct = {
        'postid': post.id,
        'title':post.title,
        'permaLink':link,
        'description':description,
        'mt_text_more':mt_text_more,
        'mt_convert_breaks':post.text_filter,
        'categories': [c.title for c in categories],
        'userid': post.author.id,
        'mt_allow_comments':str(mt_allow_comments)
    }
    
    if post.pub_date:
            struct['dateCreated'] = format_date(post.pub_date)
    return struct
    
def format_date(d):
    logger.debug( "format_date called...")
    if not d: return None
    #print 80*"x",fd    
    # return xmlrpclib.DateTime(d.isoformat())
    return xmlrpclib.DateTime(d.isoformat())

def setTags(post, struct):
    logger.debug( "setTags called")
    tags = struct.get('tags',None)
    if tags is None:
        post.tags = []
    else:
        # post.categories = [Category.objects.get(title__iexact=name) for name in tags]
        logger.debug(tags)

@public

@public
def mt_supportedMethods():
    """ returns the xmlrpc-server's list of supported methods"""
    logger.debug( "mt.listSupportedMethods called...")
    from blog import xmlrpc_views
    return xmlrpc_views.list_public_methods(blog.metaWeblog)

@public

@public
@authenticated()
def mt_getPostCategories(user, postid):
    """
    returns a list of categories for postid *postid*
    """
    logger.debug( "mt_getPostCategories called...")
    try:
        p = Post.objects.get(pk=postid)
        # print "Processing", p.categories.all()
        counter = 0
        res = []

        
        for c in p.categories.all():
            # print "Got post category:", c
            primary = False
            if p.primary_category_name == c:
                # print "%s is the primary category" % c
                primary=True
            res.append(
                dict(categoryName=c.title, categoryId=str(c.id), isPrimary=primary)
            )
    except:
        import traceback
        traceback.print_exc(sys.stderr)
        res = None
    
    return res

@public
def mt_supportedTextFilters():
    """ tells ecto to use markdown or whatever..."""
    logger.debug( "Called mt_supportedTextFilters")
    res = []
    for key, label in FILTER_CHOICES:
        # print "%s => %s" % (label, key)
        res.append(dict(label=label, key=key))

    return res

    
@public
@authenticated()
def mt_setPostCategories(user, postid, cats):
    """
    mt version of setpostcats
    takes a primary as argument
    """
    logger.debug( "mt_setPostCategories called...")
    logger.info("Submitted with %s" % cats)
    post = Post.objects.get(pk=postid)
    logger.debug("Old cats: %s" % post.categories.all())
    post.categories.clear()
    catlist = []
    for cat in cats:
        category = Category.objects.get(pk=cat['categoryId'])
        # print "Got", category
        if cat.has_key('isPrimary') and cat['isPrimary']:
            logger.debug("Got primary category '%s'" % cat)
            post.primary_category_name = category
        post.categories.add(category)
    logger.debug("New cats: %s" % post.categories.all())
    post.save()
    logger.debug(" mt_setPostCategories Done.")
    return True


@public
@authenticated()
def xblog_getIdList(user,blogid):
    # 
    """
    this function returns a (potentially very long)
    list of IDs of blog posts.
    """
    logger.debug( "xblog_getIdList called...")
    idlist = []
    logger.debug( "getting blog...")
    blog = Blog.objects.get(id=blogid)
    posts = blog.post_set.all()
    logger.debug( "got %d posts" % posts.count())
    for post in posts:
        idlist.append(post.id)
    
    return idlist

@authenticated(pos=0)
def wp_getUsersBlogs(user):
    logger.debug( "wp.getUsersBlogs called")
    # print "Got user", user
    usersblogs = Blog.objects.filter(owner=user)
    logger.debug( "%s blogs for %s" % (usersblogs, user))
    # return usersblogs
    res = [
    {
    'blogid':str(blog.id),
    'blogName': blog.title,
    'url': blog.get_url()
    } for blog in usersblogs
    ]
    logger.debug(res)
    return res

@authenticated(pos=1)
def wp_getOptions(user, blog_id, struct={}):
    """
    int blog_id
    string username
    string password
    struct
        string option
    return:
        array
        struct
            string desc
            string readonly
            string option
    """
    logger.debug("wp.getOptions entered")
    logger.debug("user: %s" % user)
    logger.debug("blog_id: %s" % blog_id)
    logger.debug("struct: %s" % struct)
    blog = Blog.objects.get(pk=blog_id)
    admin_url = {
        'value': urlparse.urljoin(blog.get_url(), "admin"),
        'desc': "The URL to the admin area",
        'readonly': True,
    }
    
    
    
    res = { 
        'admin_url':admin_url,
        'blog_id': { 'desc':'Blog ID', 'readonly':True, 'value': blog.id }, 
        'blog_public' : {'desc': 'Privacy access', 'readonly': True, 'value': '1' },
        'blog_tagline' : {'desc': 'Site Tagline', 'readonly': False, 'value': blog.description },
        'blog_title': {'desc': 'Site title', 'readonly': False, 'value': blog.title },
        'blog_url' : { 'desc': 'Blog Address (URL)', 'readonly': True, 'value': blog.get_url() }, 
        
    }
    
    logger.debug("res: %s" % res)
    
    return res

def wp_getTags(blog_id, user, password):
    """
    Get an array of users for the blog. [sic?]
    Parameters
    int blog_id
    string username
    string password
    Return Values
    array
    struct
    int tag_id
    string name
    int count
    string slug
    string html_url
    string rss_url
    
    [{
	  'count': '1',
	  'html_url': 'http://subcriticalorg.wordpress.com/tag/apocalypse/',
	  'name': 'apocalypse',
	  'rss_url': 'http://subcriticalorg.wordpress.com/tag/apocalypse/feed/',
	  'slug': 'apocalypse',
	  'tag_id': '135830'},
    }]
    
    """
    logger.debug("wp.getTags entered")
    ##FIXME check the user password...
    logger.debug("user: %s" % user)
    logger.debug("blog_id: %s" % blog_id)
    blog = Blog.objects.get(pk=blog_id)
    logger.debug(blog)
    ## FIXME: Tags are shared across blogs... :-/
    res = []
    for tag in Tag.objects.all():
        logger.debug("Processing %s" % tag)
        res.append({
        'count' : tag.post_set.count(),
        'html_url' : urlparse.urljoin(blog.get_url(),"%s/%s" % ("tag",tag.title)),
        'name' : tag.title,
        'rss_url': urlparse.urljoin(blog.get_url(),"%s/%s/%s" % ("tag",tag.title, 'feed')), 
        'slug':tag.title,
        'tag_id':tag.id,
        })
    
    logger.debug("res: %s" % res)
    return res
    
    
    
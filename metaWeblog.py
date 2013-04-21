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
from django.contrib.comments.models import FreeComment
from django.conf import settings
from xblog.models import Tag, Post, Blog, Author, Category, FILTER_CHOICES
from views.xmlrpc_views import public
from external.BeautifulSoup import BeautifulSoup
from ping_modes import send_pings

# import config
# import xmlrpclib.DateTime

def authenticated(pos=1):
    # tells the method that the visitor is authenticated
    def _decorate(func):
        def _wrapper(*args, **kwargs):
            username = args[pos+0]
            password = args[pos+1]
            args = args[0:pos]+args[pos+2:]
            try:
                # print "Username: ", username
                # print "Password: ", password
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                print "username %s, password %s, args %s" % (username, password, args)
                print "User.DoesNotExist"
                raise ValueError("Authentication Failure")
            if not user.check_password(password):
                print "User.check_password"
                raise ValueError("Authentication Failure")
            if not user.is_superuser:
                print "user.is_superuser"
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
    """
    print "metaWeblog_getCategories called"
    categories = Category.objects.all()
    res=[]
    for c in categories:
        struct={}
        struct['categoryName']= c.title
        struct['description'] = c.description
        struct['htmlUrl'] = ""
        struct['rssUrl'] = ""
        res.append(struct)
    return res


@public
@authenticated()
def metaWeblog_newMediaObject(user, blogid, struct):
    """ returns struct with url..."""
    print "metaWeblog_newMediaObject called"
    upload_dir = os.path.join(settings.MEDIA_ROOT,'blog_uploads',user.username)
    upload_url = "%s/%s/%s" % (settings.MEDIA_URL, 'blog_uploads', urllib.quote(user.username))
    print upload_dir
    print upload_url
    # print "Using upload", upload_url
    # print "Using upload dir", upload_dir
    if not os.path.exists(upload_dir):
        # create this directory....
        # print "Creating directory", upload_dir
        os.makedirs(upload_dir)

    
    bits       = struct['bits']
    mime       = struct['type']
    name       = struct['name']
    # print "got", mime, name
    savename   = name
    if os.path.isabs(savename):
       # some schmoe program wrote a slash at the beginning...
       savename = "." + savename # take that...

    print savename
    renametmpl = "%2d-%s"
    i          = 1
    while os.path.exists(os.path.join(upload_dir,savename)):
        savename = renametmpl % (i,savename)
        i = i + 1

    print "Saving to ",os.path.join(upload_dir,savename)
    f = open(os.path.join(upload_dir,savename),'w')
    f.write("%s" % bits)
    f.close()
    res = {}
    res['url']="%s/%s" % (upload_url,savename)
    return res


 
@public
@authenticated()
def metaWeblog_newPost(user, blogid, struct, publish):
    """ mt's newpost function..."""
    # print "metaWeblog.newPost called"
    body = struct['description']
    author = user # Author.objects.get(user=user)
    blog = Blog.objects.get(pk=blogid)
    pub_date = datetime.datetime.now()
    
    post = Post(
        title=struct['title'],
        body = body,
        create_date = pub_date,
        update_date = pub_date,
        pub_date = pub_date,
        status = publish and 'Published' or 'Draft',
        blog = blog,
        author =author
    )
    # print "Prepopulate"
    post.prepopulate()
    # print "Saving"
    post.save()
    # print "Setting Tags"
    setTags(post, struct)
    # print "Handling Pings"
    send_pings(post)
    # print "newPost finished"
    return post.id
    
@public
@authenticated()
def metaWeblog_editPost(user, postid, struct, publish):
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
        post.author = user # Author.objects.get(user=user)
    
    if publish:
      post.status = "publish"
    else:
      post.status = "draft"
      
    setTags(post, struct)
    # res = parse_technorati_tags(post.body)
    # post.prepopulate()
    post.update_date = datetime.datetime.now()
    post.save()
    # print "Handling Pings"
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
    print "metaWeblog.getPost called "
    post = Post.objects.get(pk=postid)
    # post.create_date = format_date(datetime.datetime.now())
    return post_struct(post)

@public
@authenticated(pos=2)
def blogger_getRecentPosts(user, appkey, blogid, num_posts):
    """ returns a list of recent posts """
    print "blogger.getRecentPosts called..."
    blog = Blog.objects.get(id=blogid)
    posts = blog.post_set.order_by('-pub_date')[:num_posts]
    return [post_struct(post) for post in posts]

@public
@authenticated()
def metaWeblog_getRecentPosts(user, blogid, num_posts):
    """ returns a list of recent posts..."""
    print "metaWeblog.getRecentPosts called..."
    print "user %s, blogid %s, num_posts %s" % (user, blogid, num_posts)
    blog = Blog.objects.get(id=blogid)
    posts = blog.post_set.order_by('-pub_date')[:num_posts]
    return [post_struct(post) for post in posts]
    

@public
@authenticated()
def blogger_getUserInfo(user, appkey):
    """ returns userinfo for particular user..."""
    print "blogger.getUserInfo called"
    # author = user # Author.objects.get(user=user)
    firstname = user.first_name
    lastname = user.last_name
    struct = {}
    struct['username']=user.username
    struct['firstname']=firstname
    struct['lastname']=lastname
    struct['nickname']= user.get_profile().fullname
    struct['url'] = user.get_profile().url
    struct['email'] = user.email
    struct['userid'] = str(user.id)
    return struct

@public
@authenticated()
def blogger_getUsersBlogs(user, appkey):
    print "blogger.getUsersBlogs called"
    # print "Got user", user
    usersblogs = Blog.objects.filter(owner=user)
    print usersblogs, "blogs for ", user
    # return usersblogs
    res = [
    {
    'blogid':str(blog.id),
    'blogName': blog.title,
    'url': blog.get_url()
    } for blog in usersblogs
    ]
    print res

    return res

@public
@authenticated()
def metaWeblog_getUsersBlogs(user, appkey):
  # the original metaWeblog API didn't include this
  # it was added in 2003, once blogger jumped ship from using
  # the blogger API
  # http://www.xmlrpc.com/stories/storyReader$2460
  print "metaWeblog.getUsersBlogs called"
  usersblogs = Blog.objects.filter(owner=user)
  print usersblogs, "blogs for ", user
  # return usersblogs
  res = [
    {
      'blogid':str(blog.id),
      'blogName': blog.title,
      'url': blog.get_url()
    } for blog in usersblogs
    ]
  print res
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
    print "blogger.deletePost called"
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
    print "mt_getCategoryList called"
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
    print "post_struct called"
    link = full_url(post.get_absolute_url())
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
    print "format_date called..."
    if not d: return None
    #print 80*"x",fd    
    # return xmlrpclib.DateTime(d.isoformat())
    return xmlrpclib.DateTime(d.isoformat())

def setTags(post, struct):
    print "setTags called"
    tags = struct.get('tags',None)
    if tags is None:
        post.tags = []
    else:
        # post.categories = [Category.objects.get(title__iexact=name) for name in tags]
        print tags

@public

@public
def mt_supportedMethods():
    """ returns the xmlrpc-server's list of supported methods"""
    print "mt.listSupportedMethods called..."
    from blog import xmlrpc_views
    return xmlrpc_views.list_public_methods(blog.metaWeblog)

@public

@public
@authenticated()
def mt_getPostCategories(user, postid):
    """
    returns a list of categories for postid *postid*
    """
    print "mt_getPostCategories called..."
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
    print "Called mt_supportedTextFilters"
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
    print "mt_setPostCategories called..."
    # print "Submitted with", cats
    post = Post.objects.get(pk=postid)
    # print "Old cats:", post.categories.all()
    post.categories.clear()
    catlist = []
    for cat in cats:
        category = Category.objects.get(pk=cat['categoryId'])
        # print "Got", category
        if cat.has_key('isPrimary') and cat['isPrimary']:
            # print "Got primary category", cat
            post.primary_category_name = category
        post.categories.add(category)
    # print "New cats:", post.categories.all()
    post.save()
    # print "Done."
    return True


@public
@authenticated()
def xblog_getIdList(user,blogid):
    # 
    """
    this function returns a (potentially very long)
    list of IDs of blog posts.
    """
    print "xblog_getIdList called..."
    idlist = []
    print "getting blog..."
    blog = Blog.objects.get(id=blogid)
    posts = blog.post_set.all()
    print "got %d posts" % posts.count()
    for post in posts:
        idlist.append(post.id)
    
    return idlist
        
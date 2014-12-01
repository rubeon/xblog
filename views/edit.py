#!/usr/bin/env python
# encoding: utf-8
"""
edit.py

Created by Eric Williams on 2007-04-09.
"""

from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context, loader
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.contrib import messages


# from xcomments.models import FreeComment
from django import forms 
from django.http import HttpResponseRedirect, HttpResponse, Http404
from xblog.models import Post, PostForm

import logging
logger = logging.getLogger(__name__)

#    class PublicFreeCommentForm(newforms.Form):
#        person_name = newforms.CharField(label="Your Name")
#        person_url = newforms.CharField(label="Web Site", required=False)
#        person_email = newforms.EmailField(label="Email Address")
#        comment = newforms.CharField(widget=newforms.Textarea(attrs={'rows':10, 'cols':50}, ) )
#        options = newforms.CharField(widget=newforms.HiddenInput)
#        target = newforms.CharField(widget=newforms.HiddenInput)
#        gonzo = newforms.CharField(widget=newforms.HiddenInput)
#

@login_required
def content_list(request, **kwargs):
    """
    This provides a list of published content...
    """
    logger.debug("content_view entered")
    c = RequestContext(request)
    
    # get a post_list
    site = get_current_site(request)

    post_list = Post.objects.all().order_by('-pub_date')
    logger.debug(post_list)
    
    c['post_list'] = post_list
    t = loader.get_template("xblog/content_list.html")
    return HttpResponse(t.render(c))
    

@login_required
def edit_post_inline(request, **kwargs):
    """
    This provides ajax queries with an edit form...
    """
    logger.debug("edit_post_inline entered")
    p = Post.objects.get(slug=kwargs['slug'])
    # if request.POST:

@login_required
def preview_post(request, **kwargs):
    """
    takes the go-get-me data from the URL, and returns the formatted version of it for previewin'
    """
    logger.debug("preview_post called")
    logger.debug(kwargs)
    
    p = Post.objects.get(slug=kwargs['slug'])
    
    logger.info("preview_post showing %s" % p)
    # data = p.get_full_body()
    
    # put the post into a context for the template render...
    logger.debug("opening template")
    c = RequestContext(request)
    c['object'] = p
    t = loader.get_template('includes/post_template.txt')
    
    return HttpResponse(t.render(c))
    

@login_required
def set_publish(request, **kwargs):
    logger.debug("set_published entered")
    # logger.debug(request.GET)
    if request.GET.has_key('value'):
        new_status = request.GET['value']
        logger.debug("set_published: %s" % new_status )
        p = Post.objects.get(slug=kwargs['slug'])
        p.status = new_status
        p.save()
        return HttpResponse("<p>%s saved</p>" % p.title)
    else:
        logger.warn("Invalid set_status: %s" % request.GET['value'])
        return "<p>Invalid request</p>"

@login_required
def edit_post(request, **kwargs):
    logger.debug("edit_post: %s" % locals())
    # PostForm = forms.form_for_model(Post)
    p = Post.objects.get(slug=kwargs['slug'])
    if request.POST:
        logger.info("Got POST...")
        # newdata = request.POST.copy()
        # newform = PostForm(newdata)
        # newform.base_fields['body'].widget=forms.Textarea(attrs={'rows':10, 'cols':50})
        form = PostForm(request.POST)
                
        if form.is_valid():
            logger.info("Form is valid, saving...")
            logger.debug(form)
            model_instance = form.save(commit=False)
            model_instance.update_date = timezone.now()
            model_instance.save()
            # messages.add_message(request, messages.INFO, "Saved '%s'" % model_instance.title)
            messages.info(request, "Saved '%s'" % model_instance.title)
            return HttpResponseRedirect(model_instance.get_absolute_url())
            
        else:
            logger.warn("Form data invalid; showing again")
            logger.warn(form.errors)
            logger.debug(form)
            c = RequestContext(request)
            c['form']=f = PostForm(instance=p)
            t = loader.get_template('xblog/edit_post.html')
            # messages.add_message(request, messages.ERROR, form.errors)
            messages.error(request, form.errors)
            return HttpResponse(t.render(c))
            
    else:
        # f = forms.form_for_instance(p,form=PostForm)()
        f = PostForm(instance=p)
        c = RequestContext(request)
        c['form']=f
        t = loader.get_template('xblog/edit_post.html')
        return HttpResponse(t.render(c))
    

@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # commit=False means the form doesn't save at this time.
            # commit defaults to True which means it normally saves.
            model_instance = form.save(commit=False)
            model_instance.update_date = timezone.now()
            model_instance.save()
            # messages.add_message(request, messages.INFO, "Added '%s'" % model_instance.title)
            messages.info(request, "Added '%s'" % model_instance.title)
            return redirect(model_instance.get_absolute_url())
        else:
            # messages.add_message(request, messages.ERROR, form.errors)
            messages.error(request, form.errors)
            c = RequestContext(request)
            c['form']=form
            t = loader.get_template('xblog/edit_post.html')
            return HttpResponse(t.render(c))
    else:
        form = PostForm()

    return render(request, "xblog/edit_post.html", {'form': form})
    

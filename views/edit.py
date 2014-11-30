#!/usr/bin/env python
# encoding: utf-8
"""
edit.py

Created by Eric Williams on 2007-04-09.
"""

from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context, loader
from django.shortcuts import render, redirect
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
    

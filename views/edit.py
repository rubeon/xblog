#!/usr/bin/env python
# encoding: utf-8
"""
edit.py

Created by Eric Williams on 2007-04-09.
"""

from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context, loader
# from xcomments.models import FreeComment
from django import forms 
from django.http import HttpResponseRedirect, HttpResponse, Http404
from xblog.models import Post

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
def edit_post(request, slug):
    print "edit_post called..."
    PostForm = forms.form_for_model(Post)
    p = Post.objects.get(slug=slug)
    if request.POST:
        print "Got post..."
        newdata = request.POST.copy()
        newform = PostForm(newdata)
        newform.base_fields['body'].widget=forms.Textarea(attrs={'rows':10, 'cols':50})
        
        
        if newform.is_valid():
            newform.save()
            return HttpResponseRedirect('..')
        else:
            c = RequestContext(request)
            c['form']=f()
            t = loader.get_template('xblog/edit_post.html')
            return HttpResponse(t.render(c))
            
    else:
        f = forms.form_for_instance(p,form=PostForm)()
        c = RequestContext(request)
        c['form']=f
        t = loader.get_template('xblog/edit_post.html')
        return HttpResponse(t.render(c))
    

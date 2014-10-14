#!/usr/bin/env python
# encoding: utf-8
"""
templatetags.py

Created by Eric Williams on 2007-03-10.
"""

from xblog.models import LinkCategory, Link, Post
from django.template import Library,Node

import logging
logger = logging.getLogger("xblog")

register = Library()

def get_blogroll(parser, token):
    """
    {% get_blogroll %}
    """
    logger.debug("get_blogroll called")
    return BlogRoll()
    
def get_blog_months(parser, token):
    """{% get_blog_months %}"""
    logger.info("get_blog_months called")
    return MonthMenuObject()
    
class MonthMenuObject(Node):
    def render(self, context):
        logger.debug("MonthMenuObject.reder called")
        try:
            context['blog_months'] = Post.objects.dates("pub_date", "month")
        except AssertionError:
            logging.warn("Version >= 1.6  using Post.objects.datetimes")
            context['blog_months'] = Post.objects.datetimes("pub_date", "month")
        return ''

class BlogRoll(Node):
    """A Blogroll object...."""
    
    def render(self, context):
        logger.debug("BlogRoll.render called")
        context['blogroll_categories'] = LinkCategory.objects.all()
        return ''
        
        
logger.info("%s:Registering 'get_blogroll'" % __file__)
register.tag('get_blogroll', get_blogroll)
logger.info("%s:Registering 'get_blog_months'" % __file__)
register.tag('get_blog_months', get_blog_months)
# -*- coding: utf-8 -*-

import markdown

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

from django.utils.safestring import mark_safe

register = template.Library()

import logging
logger = logging.getLogger("xblog")

@register.filter(is_safe=True)
@stringfilter
def xblog_markdown(value):
    """
    filters value through markdown
    """
    logger.debug("xblog_markdown called")
    extensions = ["nl2br",]
    res = markdown.markdown(force_unicode(value), extensions, safe_mode=True, enable_attributes=False)
    return mark_safe(res)
    
    
logger.info("%s:Registering 'xblog_markdown'" % __file__)

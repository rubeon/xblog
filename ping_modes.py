#!/usr/bin/env python
# encoding: utf-8
"""
trackbacktest.py

Created by Eric Williams on 2007-04-04.
"""
from xml.sax.handler import ContentHandler
from xml.sax import parseString, SAXParseException
from xblog.models import Pingback, Post
from django.conf import settings
import datetime
from django.http import HttpResponseRedirect, HttpResponse, Http404
import xmlrpclib
import urllib, re
from external.BeautifulSoup import BeautifulSoup as bs

def process_trackback(request, slug):
    if request.method == 'POST':
        print "Got a trackback, methinks...", slug
        source_uri = request.POST['url']
        try:
            post = Post.objects.get(slug__exact=slug)
            print "post: ", post.title
            target_uri = post.get_absolute_uri()
        except Exception, e:
            import sys, traceback
            traceback.print_exc(sys.stderr)
            return False
        print "From:", source_uri
        print "To:", target_uri
        print "Post:", post.title
        res, message = trackback_ping(source_uri, target_uri, check_spam=True)
        if res:
            return HttpResponse("""
            <?xml version="1.0" encoding="iso-8859-1"?>
            <response>
            <error>0</error>
            </response>
            """)
            
        else:
            return HttpResponse("""
            <?xml version="1.0" encoding="iso-8859-1"?>
            <response>
            <error>1</error>
            <message>%s</message>
            </response>
            """ % message)
    else:
        return HttpResponse( "Ping?")
        

def pingback_ping(source_uri, target_uri, check_spam=True, post=None, outgoing=False):
    """
    Pingback interface
    for outgoing pings, set keyword arguments post (post object) and
    outgoing=True
    """
    print "pingback_ping called..."
    print "Ping from: ",source_uri
    print "Ping to: ", target_uri
    # check for dupes...
    
    try:
        pb = Pingback.objects.filter(source_url=source_uri).filter(target_url=target_uri)
        for x in pb:
            print "-",x
        if pb.count() > 0:
            # it's a dupe, just ignore it.
            print "Got this pingback already, homey."
            return False
    except Exception,e:
        import traceback, sys
        print traceback.print_exc(sys.stderr)
        return False, sys.exc_info()[0]
            
    # print "%s -> %s" (source_uri, target_uri)
    if outgoing:
        
        p = post
        if source_uri[0]=="/":
          # this is a site-absolute url, let's make it a real one...
          source_uri = settings.SITE_URL + source_uri[1:]
          
        print "Sending ping..."
        pingback_address = get_pingback_url(target_uri)
        
        if pingback_address:
            try:
                # we got *something*
                print "Sending ping request %s -> %s" % (source_uri, pingback_address)
                s = xmlrpclib.ServerProxy(pingback_address)
                res = s.pingback.ping(source_uri, target_uri)
                print "Got back", res
                struct = {}
                struct['author_name'] = post.author.get_profile().fullname
                struct['source_url']  = source_uri
                struct['target_url']  = target_uri
                struct['title'] = post.title
                print struct
            except Exception,e:
                import traceback, sys
                traceback.print_exc(sys.stderr)
                return False, sys.exc_info()[0]
    
    else:
        # this is an incoming ping-a-ling
        slug = slug_from_uri(target_uri)
        print "got %s" % slug
        
        try:
            if not post:
                p = Post.objects.get(slug__iexact=slug)
            else:
                p = post    
        except:
            print "No post for", slug
            return False
        print "Got trackback request for '%s'" % p.title
        # title = p.has_key('title') and request.POST['title'] or ''
        title = p.title
        # excerpt = p.has_key('excerpt') and request.POST['excerpt'] or ''
        is_spam, struct = confirm_pingback(source_uri, target_uri, check_spam = check_spam)
        print "is_spam", is_spam
        print "struct", struct
        if check_spam and is_spam:
            # print "SPAM!!!11!"
            return "Sorry, buddy, go peddle your v1agra somewhere else"
    # ok, let's get this started
    print "Creating Pingback..."
    try:
        pb              = Pingback(
            author_name = struct['author_name'],
            title       = struct['title'],
            source_url  = struct['source_url'],
            target_url  = struct['target_url'],
            is_public   = True,
            pub_date    = datetime.datetime.now(),
            post = p,
        )
        
        print "Saving pingback..."

        # print p.post_id
        # pb.post = p
        print "Added post, saving PB again...(!)"
        pb.save()
        res = "Pingback to '%s' successfully registered." % title
        return res

    except Exception, e:
        print e
        return False

        
def slug_from_uri(uri):
    # take the re from the uri.
    # pat = "http://ericbook.local:8000/blog/2007/mar/05/a-shadow-world-within-a-world/"
    pat = r"%sblog/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$" % settings.SITE_URL
    #print pat
    c = re.compile(pat)
    m = c.match(uri)
    if m:
        slug = m.groupdict()['slug']
    else:
        slug = ""
    # print "got slug...", slug
    return slug
    
def get_pingback_url(target_url):
    """
    Grabs an page, and reads the pingback url for it.
    """
    print "get_pingback_url called..."
    print "grabbing", target_url
    html = urllib.urlopen(target_url).read()
    print "Got %d bytes" % len(html)
    soup = bs(html)
    # check for link tags...
    pbaddress = None
    for l in soup.findAll('link'):
        if l.get('rel','') == 'pingback':
            pbaddress = str(l.get('href'))
            print "Got", pbaddress
            
    return pbaddress
    
def confirm_pingback(target_url, search_url, check_spam=True):
    # target url must contain search_url
    # returns bool is_spam, struct  
    print "Loading external page", target_url
    text = urllib.urlopen(target_url).read()
    # print "Got:"
    # print text
    soup = bs(text)
    print "Checking for URL", search_url
    for a in soup.findAll('a'):
        if not check_spam or a.get('href') == search_url:
            print "Got", a.get('href')
            struct = {}
            # read the author's name, if possible...
            struct['author_name'] = ''
            struct['source_url']  = target_url
            struct['target_url']  = search_url
            struct['title'] = str(soup.html.head.title.string)
            print "returning pingback"
            return False, struct
    # didn't find it...sod off, spamboy!
    return True, None

def send_pings(post):
    if post.status=='publish':
        # check for outgoing links.
        target_urls = []
        # print post.body
        soup = bs(post.get_formatted_body())
        
        for a in soup.findAll('a'):
            target_url = a.get('href',None)
            if target_url:
                print "Got URL:", a.get('href')
                target_urls.append(target_url)
        
        print "Checking out %d url(s)" % len(target_urls)
        for url in target_urls:
            pb_urls, tb_urls = get_ping_urls(url)
            for pb in pb_urls:
                pingback_ping(post.get_absolute_url(), url, post=post, outgoing=True)
            for tb in  tb_urls:
                trackback_ping(post.get_absolute_url(), tb, post=post, outgoing=True)

def trackback_ping(source_uri, target_uri, check_spam=True, post=None, outgoing=False):
    """
    send an MT-style trackback-ping to the given URL, which should be the 
    trackback URL of a blog post
    """

    print "trackback_ping called..."
    if source_uri[0]=="/":
       # this is a site-absolute url, let's make it a real one...
       source_uri = settings.SITE_URL + source_uri[1:]
                
    print "Ping from: ",source_uri
    print "Ping to: ", target_uri
    # check for dupes...

    try:
        print "Checking for dupes..."
        pb = Pingback.objects.filter(source_url=source_uri).filter(target_url=target_uri)
        for x in pb:
            print "-",x
        if pb.count() > 0:
            # it's a dupe, just ignore it.
            print "Got this pingback already, homey."
            return False, "Got this pingback already, homey."
    except Exception,e:
        import traceback, sys
        print traceback.print_exc(sys.stderr)

    print "Moving along..."
    print "%s -> %s" % (source_uri, target_uri)
    if outgoing:
        print "outbound ping"
        # trackbacks send a POST to the target URL with:
        # title=title
        # url = post.get_absolute_url
        # excerpt = ??
        # blog_name = post.blog.title
        p = post
        print "Sending trackback..."
        # pingback_address = get_pingback_url(target_uri)
        if target_uri:
            try:
                # we got *something*
                print "Sending trackback request..."
                # s = xmlrpclib.ServerProxy(pingback_address)
                # res = s.pingback.ping(source_uri, target_uri)
                data = dict(title=p.title, url=source_uri, excerpt=p.summary,blog_name=p.blog.title)
                res = urllib.urlopen(target_uri, urllib.urlencode(data)).read()
                print "Got back", res
                struct = {}
                try:
                    struct['author_name'] = post.author.get_profile().fullname
                except:
                    struct['author_name']=post.author.username
                struct['source_url']  = source_uri
                struct['target_url']  = target_uri
                struct['title'] = post.title
            except Exception,e:
                import traceback, sys
                traceback.print_exc(sys.stderr)
                return False, sys.exc_info()[0]

    else:
        # this is an incoming ping-a-ling
        print "Inbound ping..."
        print "Checking", target_uri
        slug = slug_from_uri(target_uri)
        print "got %s" % slug

        try:
            if not post:
                p = Post.objects.get(slug__iexact=slug)
            else:
                p = post    
        except:
            print "No post for", slug
            return False, "Post not found"
        print "Got trackback request for '%s'" % p.title
        # title = p.has_key('title') and request.POST['title'] or ''
        title = p.title
        # excerpt = p.has_key('excerpt') and request.POST['excerpt'] or ''
        is_spam, struct = confirm_pingback(source_uri, target_uri, check_spam = check_spam)
        print "is_spam", is_spam
        print "struct", struct
        if check_spam and is_spam:
            # print "SPAM!!!11!"
            return False, "Sorry, buddy, go peddle your v1agra somewhere else"
    # ok, let's get this started
    print "Creating Pingback..."
    try:
        pb              = Pingback(
            author_name = struct['author_name'],
            title       = struct['title'],
            source_url  = struct['source_url'],
            target_url  = struct['target_url'],
            is_public   = True,
            pub_date    = datetime.datetime.now(),
            post = p,
        )

        print "Saving pingback..."

        # print p.post_id
        # pb.post = p
        print "Added post, saving PB again...(!)"
        pb.save()
        print "saved PBw"
        res = "Pingback to '%s' successfully registered." % pb.title
        print res
        return True, res

    except Exception, e:
        print e
        return False, "Unknown Error"

    
    
def get_ping_urls(url):
    """
    returns a two-tuple of lists, ([pingback urls],[trackback urls])
    """
    ping_urls = []
    tb_urls = []
    
    txt = urllib.urlopen(url).read()
    print "Got %d bytes" % len(txt)
    soup = bs(txt)
    # walk through the links, looking for ping-entries
    
    for a in soup.findAll('link'):
        print a
        rel = a.get('rel')
        if rel == 'pingback':
            print "Got pingback URL:", a.href
            ping_urls.append(a.get('href'))
    
    # now do t he trackbacks...
    tb_re=re.compile('(<rdf:RDF .*?</rdf:RDF>)')
    rdfdata = RDF()
    for x in tb_re.findall(txt.replace('\n',' ')):
        try:
            parseString(x, rdfdata)
            # print rdf.ids
            print "URL:", rdfdata.attrs.get('dc:identifier')
            print "Trackback URL:", rdfdata.attrs.get('trackback:ping')
            tb_urls.append(rdfdata.attrs.get('trackback:ping'))
        except Exception,e:
            import traceback, sys
            traceback.print_exc(sys.stdout)
    
    return ping_urls, tb_urls


class RDF(ContentHandler):
    """ xml -> dictionary of {dc:identifier => trackback:ping|rdf:about}

    Parse a given html page, and retrieve the rdf:about information associated
    with a given href.
    """
    attrs = {}
    ids = {}
    def startElement(self, name, attrs):
        # print name, attrs
        if name == 'rdf:Description':
            attrs=dict(attrs)
            self.attrs = attrs
            # print "ATTRS:", attrs
            if attrs.has_key('dc:identifier'):
                # print "ID:", attrs['dc:identifier']
                if attrs.has_key('trackback:ping'):
                    self.ids[attrs['dc:identifier']] = attrs['trackback:ping']
                elif attrs.has_key('about'):
                    self.ids[attrs['dc:identifier']] = attrs['about']
                elif attrs.has_key('rdf:about'):
                    self.ids[attrs['dc:identifier']] = attrs['rdf:about']


if __name__=='__main__':
    tb_test_url = "http://jaksrv.local/mt/2007/03/test_fo_die_trackabacakas.html"
    ping_test_url = "http://rubeon.ath.cx/wp/?p=29"
    print get_ping_urls(tb_test_url)
    print get_ping_urls(ping_test_url)
    
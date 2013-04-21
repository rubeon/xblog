from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User 
from django.core.mail import mail_managers, send_mail
from django.utils.text import truncate_html_words
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from external import fuzzyclock
import datetime
import time
import os
import string


from mimetypes import guess_type
from external.markdown import Markdown
from external.smartypants import smartyPants
from external.postutils import SlugifyUniquely
from external.BeautifulSoup import BeautifulSoup

# import xblog.metaWeblog 


# Create your models here.

STATUS_CHOICES=(('draft','Draft'),('publish','Published'),('private','Private'))
FILTER_CHOICES=(
    ('markdown','Markdown'),
    ('html','HTML'),
    ('convert linebreaks','Convert linebreaks')
)



# text filters


def xmlify(data):
    return data
    replaced=False
    for let in data:
        # fix non-unicodies.
        if ord(let) > 127:
            replaced=True
            print "Replacing %s -> &%d;" % (let,ord(let) )
            data = data.replace(let,"&#%d;" % ord(let))

    return data


filters={}
def get_markdown(data):
    m = Markdown(data, 
                     extensions=['footnotes'],
                     # extension_configs= {'footnotes' : ('PLACE_MARKER','~~~~~~~~')},
                     encoding='utf8',
                     safe_mode = False
                     )
    res = m.toString()
    res = smartyPants(res, "1qb")
    return res
    
filters['markdown']=get_markdown

def get_html(data):
    # just return it.
    # maybe tidy it up or something...
    data = smartyPants(data, "1qb")
    return data

filters['html']=get_html

def convert_linebreaks(data):
    data = data.replace("\n", "<br />")
    return smartyPants(data,"1qb")

filters['convert linebreaks']=convert_linebreaks
filters['__default__']=convert_linebreaks


class LinkCategory(models.Model):
    """Categories for  the blogroll"""
    title = models.CharField(blank=True, max_length=255)
    description = models.TextField(blank=True)
    visible = models.BooleanField(default=True)
    blog = models.ForeignKey('Blog')
    display_order = models.IntegerField(blank=True, null=True)
    
    class Admin:
        list_display = ('title',)
        search_fields = ('title',)

    def __str__(self):
        return str(self.title)
    __repr__=__str__

class Link(models.Model):
    """Blogroll Struct"""
    url = models.URLField(blank=True, verify_exists=True)
    link_name = models.CharField(blank=True, max_length=255)
    link_image = models.ImageField(upload_to="blog_uploads/links/", height_field='link_image_height', width_field='link_image_width',blank=True)
    link_image_height = models.IntegerField(blank=True, null=True)
    link_image_width = models.IntegerField(blank=True, null=True)
    
    description = models.TextField(blank=True)
    visible = models.BooleanField(default=True)
    blog = models.ForeignKey('Blog')
    rss = models.URLField(blank=True, verify_exists=True)
    
    category = models.ForeignKey('LinkCategory')
    
    class Admin:
        #list_display = ('',)
        #search_fields = ('',)
        list_display = ('url', 'description')

    def __str__(self):
        return "%s (%s)" % (self.link_name, self.url)
    
    __repr__=__str__

class Pingback(models.Model):
    """ Replies are either pingbacks """
    
    author_name = models.CharField(blank=True, max_length=100)
    author_email = models.EmailField(blank=True)
    post = models.ForeignKey('Post')
    title = models.CharField(blank=True, max_length=255)
    body = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    
    source_url = models.URLField(blank=True, verify_exists=True)
    target_url = models.URLField(blank=True, verify_exists=False)
    pub_date = models.DateTimeField(blank=True, default=datetime.datetime.now())
    mod_date = models.DateTimeField(blank=True, default=datetime.datetime.now())
    

    class Admin:
        # list_display = ('pub_date', 'title', 'source_url','target_url')
        search_fields = ('title','pub_date',)
        list_filter = ['pub_date', 'is_public']

    def __str__(self):
        return "Reply %s -> %s" % (self.source_url,self.target_url)

    def __repr__(self):
        return "%s (%s - %s)" % (self.title, self.source_url, self.target_url)

    def save(self):
        super(self.__class__, self).save()
        mail_subject = "New Pingback from %s" % self.title.strip()
        mail_body = """        
        
Source URL: %s
Target URL: %s
      Time: %s
            """ % (self.source_url, self.target_url, self.pub_date)
            
        print mail_subject
        print mail_body
        # mail_managers(mail_subject, mail_body, fail_silently=False)
        send_mail(mail_subject, mail_body, "eric@xoffender.de", [self.post.author.email])
        
class Tag(models.Model):
    """(Tag description)"""
    title = models.CharField(blank=True, max_length=100)

    class Admin:
        list_display = ('title',)
        search_fields = ('title',)

    def __str__(self):
        # return "%s (%s - %s)" % (self.title, self.source_url, self.target_url)
        return self.title


class Author(models.Model):
    """User guy"""
    fullname = models.CharField(blank=True, max_length=100)
    url = models.URLField(blank=True, verify_exists=True)
    avatar = models.ImageField(blank=True, upload_to="users/avatars/", height_field='avatar_height', width_field='avatar_width')
    user = models.ForeignKey(User, unique=True)
    about = models.TextField(blank=True)
    avatar_height = models.IntegerField(blank=True, null=True)
    avatar_width = models.IntegerField(blank=True, null=True)
    class Admin:
        # list_display = ('',)
        # search_fields = ('',)
        pass

    def __str__(self):
        return "%s (%s)" % (self.fullname,self.user.username)



class Category(models.Model):
    """Categories for Blog entries"""
    title = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=100)
    blog = models.ForeignKey("Blog")

    class Admin:
        list_display = ('title','blog')
        search_fields = ('title',)

    def __str__(self):
        return self.title


class Post(models.Model):
    """A Blog Entry, natch"""
    # metadata
    pub_date = models.DateTimeField(blank=True, default=datetime.datetime.now())
    update_date = models.DateTimeField(blank=True, auto_now=True)  # default=datetime.datetime.now())
    create_date = models.DateTimeField(blank=True, auto_now_add=True)  # default=datetime.datetime.now())
    enable_comments = models.BooleanField(default=True)
    # post content 
    title = models.CharField(blank=False, max_length=255)
    slug = models.SlugField(prepopulate_from=("title",), max_length=100)
    body = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    categories = models.ManyToManyField(Category)
    primary_category_name = models.ForeignKey(Category, related_name='primary_category_set', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    blog = models.ForeignKey('Blog')
    # authors = models.ManyToManyField(Author)
    author = models.ForeignKey(User)
    status = models.CharField(blank=True, null=True, max_length=32, choices=STATUS_CHOICES, 
        radio_admin=True,default="Draft")
    
    # filter to display when "get_formatted_body" is called.
    text_filter = models.CharField(blank=True, max_length=100, choices=FILTER_CHOICES, default='__default__')


    class Admin:
        # list_display = ('title',)
        list_display = ('title','pub_date','author','status')
        search_fields = ('title','body','slug')
        date_hierarchy = 'pub_date'
        list_filter = ['author','pub_date', 'status', 'tags', 'categories']
        
        fields = (
          (None, {'fields':('title','slug',)}),
          ('Date & Time',{'fields':("pub_date",)}),
          (None, {'fields':('text_filter','body',)}),
          ('Metadata', {'fields':('tags','categories','blog','author','status','enable_comments')}),
          ('Extras', {'fields':('update_date','create_date', 'summary',
                                'primary_category_name', ), 'classes':'collapse'}),
        )
        

    def __str__(self):
        return self.title
        
    def comment_period_open(self):
        """ determines if a post is too old..."""
        # uncomment rest of line to set limit at 30 days.
        # Sometimes I get hits on older entries, so I'll leave this one for now.
        return self.enable_comments # and datetime.datetime.today() - datetime.timedelta(30) <= self.pub_date
        
    
    def prepopulate(self):
        if not self.slug or self.slug=='':
            self.slug = SlugifyUniquely(self.title, self.__class__)
            
        if not self.summary or self.summary == '':
            # do an auto-summarize here.
            # now what could that be?
            pass

    def handle_technorati_tags(self):
        # takes the post, and returns the technorati links in them...
        # from ecto:
        start_tag = "<!-- technorati tags start -->"
        end_tag = "<!-- technorati tags end -->"
        text = self.body
        start_idx = text.find(start_tag) + len(start_tag)
        end_idx = text.find(end_tag)
        if start_idx==-1 or end_idx ==-1:
            return
        #print "Got target text: starts at", start_idx
        #print "Ends at", end_idx
        #print "Got:", text[start_idx:end_idx]
        soup = BeautifulSoup(text)
        tags = []
        for a in soup.findAll('a'):
            if "http://www.technorati.com/tag/" in a.get('href'):
                # seems to be taggy
                tags.append(a.string)
                
        print tags
        taglist = []
        for tag in tags:
            # try to find the tag
            try:
                t = Tag.objects.get(title__iexact=tag)
                print "Got '%s'" % t
            except:
                # not found, create tag
                print "Creating '%s'" % tag
                t = Tag(title = tag)
                t.save()

            taglist.append(t)
        
        self.tags = taglist

            
    def save(self):
        # convert this crapola to unicode
        # self.body = self.body.decode('utf-8')
        # print self.body
        #if not self.id:
        #    # replace self.name with your prepopulate_from field
        #    self.body = xmlify(self.body)
        #    self.title = xmlify(self.title)
            
        if not self.slug or self.slug=='':
            self.slug = SlugifyUniquely(self.title, self.__class__)
            
        # regen summary...
        
        self.summary=truncate_html_words(filters.get(self.text_filter, convert_linebreaks)(self.body), 50)
        
        # save to create my ID for the manytomany thing
        super(self.__class__, self).save()
        # self.handle_technorati_tags()
        # save again :-/
        # super(self.__class__, self).save()
        # check the outgoing pings...
        
    def get_archive_url(self):
        # returns the path in archive
        archive_url = settings.SITE_URL + "blog/archive/"
        return archive_url
        
    def get_year_archive_url(self):
        return self.pub_date.strftime( settings.SITE_URL + "blog/%Y/").lower()
        
    def get_month_archive_url(self):
        return self.pub_date.strftime(settings.SITE_URL +"blog/%Y/%b").lower()
        
    def get_day_archive_url(self):
        return self.pub_date.strftime(settings.SITE_URL +"blog/%Y/%b/%d").lower()

    def get_post_archive_url(self):
        return self.get_absolute_url()  
        
    def get_trackback_url(self):
        # returns url for trackback pings.
        # return self.get_absolute_url() + "trackback/"
        # return "".join([settings.SITE_URL,, str(self.id)]) + "/"
        return settings.SITE_URL + self.get_absolute_url()[1:] + "trackback/"
    
    def get_absolute_uri(self):
        # returns a url for the interweb
        blogid = self.blog.id
        datestr = self.pub_date.strftime("%Y/%b/%d")
        
        # print self.slug
        return settings.SITE_URL + "blog/%s/%s/" % (datestr.lower(), self.slug) 


    def get_absolute_url(self):
        blogid = self.blog.id
        datestr = self.pub_date.strftime("%Y/%b/%d")
        
        # print self.slug
        return settings.SITE_URL +"blog/%s/%s/" % (datestr.lower(), self.slug) 

    def get_site_url(self):
        """
        this is the site_url
        """
        datestr = self.pub_date.strftime("%Y/%b/%d")
        return "/".join(['/blog', datestr.lower(), self.slug]) + "/"
        
    
    def get_full_body(self):
        """ same as get_formatted_body, but removes <-- more --> tags."""
        b = self.body.replace('<!--more-->','')
        textproc = filters.get(self.text_filter, convert_linebreaks)
        b = textproc(b)
        return b
        
    # newness
    get_full_body.allow_tags = True
    
    def get_formatted_body(self, split=True):
        """ returns the markdown-formatted version of the body text"""
        # check for 'more' tag
        if split and self.body.find('<!--more-->') > -1:
            # this is split.
            b = self.body.split('<!--more-->')[0]
            splitted = True
        else:
            b = self.body
            splitted = False
            
        textproc = filters.get(self.text_filter, convert_linebreaks)
        b = textproc(b)
        if splitted:
            b += """<p><a href="%s">Continue reading "%s"</p>""" % (self.get_absolute_url(), self.title)

        # print res
        return b
    
    # newness?
    get_formatted_body.allow_tags = True
            
    def get_fuzzy_pub_date(self):

        h = self.pub_date.hour
        m = self.pub_date.minute
        fc = fuzzyclock.FuzzyClock()
        fc.setHour(h)
        fc.setMinute(m)
        res =  string.capwords(fc.getFuzzyTime())
        return res
        
    def get_pingback_count(self):
        return len(self.pingback_set.all())
        
class Blog(models.Model):
    """ For different blogs..."""
    title = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User)
    site = models.ForeignKey(Site)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Admin:
        list_display = ('title','owner')
        search_fields = ('title',)

    def __str__(self):
        return self.title

    def get_url(self):
        return "".join([settings.SITE_URL,"blog","/", str(self.id)]) + "/"
        
        
        
#class PodcastChannel(models.Model):
#    """ model for the podcast, sorta like a blog..."""
#    title = models.CharField(blank=True, max_length=200)
#    slug = models.SlugField(prepopulate_from=("title",))
#    description = models.TextField(blank=True)
#    link = models.URLField(blank=True, verify_exists=False)
#    language = models.TextField(blank=True, default="en-us")
#    copyright = models.TextField(blank=True)
#    # lastBuildDate = models.DateTimeField(blank=True, default=datetime.datetime.now())
#    # lastPubDate = models.DateTimeField(blank=True, default=datetime.datetime.new())
#    # author = models.CharField(blank=True, max_length=100)
#    subtitle = models.TextField(blank=True)
#    summary = models.TextField(blank=True)
#    owner = models.ForeignKey(Author)
#    explicit = models.BooleanField(default=False)
#    image = models.ImageField(upload_to=os.path.join(settings.MEDIA_ROOT,'blog_uploads','podcasts'), height_field='image_height', width_field='image_width', blank=True)
#    image_height = models.IntegerField(blank=True, null=True)
#    image_width = models.IntegerField(blank=True, null=True)
#    
#    
#    class Admin:
#        pass
#        
#        
#    def __str__(self):
#        return "Podcast Channel: %s" % self.title
#
#class Podcast(models.Model):
#    """A Podcast episode"""
#    channel = models.ForeignKey(PodcastChannel)
#   #  categories = models.ManyToManyField(Category)
#    title = models.CharField(blank=True, max_length=200)
#    subtitle = models.TextField(blank=True)
#    summary = models.TextField(blank=True)
#    slug = models.SlugField(prepopulate_from=("title",))
#    
#    link = models.URLField(blank=True, verify_exists=False)
#    guid = models.URLField(blank=True, verify_exists=False)
#    description = models.TextField(blank=True)
#    url = models.URLField(blank=True, verify_exists=False)
#    author = models.ForeignKey(Author)
#    explicit = models.BooleanField(default=False)
#    enclosure = models.FileField(upload_to=os.path.join('blog_uploads','podcasts/') )
#    
#    pubdate = models.DateTimeField(blank=True, default=datetime.datetime.now())
#    # pub_date = pubdate
#    def get_enclosure_length(self):
#        # print "Getting enclosure length"
#        import stat
#        # returns the length of the podcast
#        s = os.stat(os.path.join(settings.MEDIA_ROOT,self.enclosure))
#        # print s[stat.ST_SIZE]
#        return s[stat.ST_SIZE]
#    
#    def get_enclosure_mime_type(self):
#        # print "Guessing mime type"
#        res =  guess_type(self.enclosure)[0]
#        print "Guessed '%s'" % res
#        return res
#    
#    class Admin:
#        #list_display = ('',)
#        #search_fields = ('',)
#        pass
#
#    def __str__(self):
#        return "Podcast: %s" % self.title
#
#    def delete(self):
#        if os.path.exists(self.enclosure):
#            os.unlink(self.enclosure)
#        
#        super(Podcast,self).delete()
#        
"""
Importing from a WordPress blog:

- get a list of authors
- get a list of categories
- get a list of posts

First, Create a local cache of all the posts.



map an author to the logged-in guy

"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from optparse import make_option
from xblog.models import Category, Blog, Post, Author
import sys
import xmlrpclib
import urllib
import getpass
import os
import BeautifulSoup
import json
import getpass
from pprint import pprint
username = "subcriticalorg"
# password = getpass.getpass()
password = open(os.path.expanduser("~/pw.txt")).read().strip()
# wp_url = "https://subcriticalorg.wordpress.com/xmlrpc.php"
# wp = xmlrpclib.ServerProxy(wp_url, use_datetime=True)

# create all the categories
INCLUDE_DRAFTS=1
date_fields = [ 'date_created',
                'date_created_gmt', 
                'post_date_gmt', 
                'post_date', 
                'post_date_gmt',
                'post_modified',
                'post_modified_gmt']
# create ALL the posts

def notify(msg):
    tmpl = "* %s\n"
    
    sys.stderr.write(tmpl % msg)
    sys.stderr.flush()

class Command(BaseCommand):
    """ Import blog posts from a remote blog """
    option_list = BaseCommand.option_list + (
            make_option("-u", "--username", dest="username", default=[], metavar="username", help="User name for remote API endpoint"),
            make_option("-a", "--all", dest="all_blogs", action="store_true", help="Import all user blogs from API endpoint"),
            make_option("-x", "--api-endpoint", dest="api_endpoint", default=None, metavar="API endpoint", help="Direct URL for remote API endpoint"),
            make_option("-p", "--password", dest="password", default=[], help="Password for remote API connection"),
            make_option("-f", "--filename", dest="filename", metavar="json_filename", help="JSON file which contains dump blog data (created with --dump)"),
            make_option("-n", "--dry-run", dest="dry_run", action="store_true", help="Do not write anything to the database"),
            make_option("-d", "--dump", dest="dump", action="store_true", help="Write retrieved data to screen in JSON format"),
        )
    args = "[blog_url] [xblog_id] [-u username] [-p password]"
    help = """ Import blog posts from a remote blog """
    
    def handle(self, *args, **options):
        """
        imports a remote blog via the WordPress API
        """
        # print args
        # print options
        blog_url = args[0]
        xblog_id = args[1]
        if options.get("dump"):
            dry_run = True
            notify("Dumping %s to screen" % args[0])

        username = options.get("username") or raw_input("Username: ").strip()
        password = options.get("password") or getpass.getpass()
        
        wp_url =  self.get_xmlrpc_url(args[0]) # "https://subcriticalorg.wordpress.com/xmlrpc.php"
        if not wp_url:
            notify("Couldn't find API link in page %s" % blog_url)
            notify("Please re-run with '-x url_to_api_endpoint'")
        wp_url = "https://subcriticalorg.wordpress.com/xmlrpc.php"
        # create the xmlrpc connection
        notify("Logging in at %s" % wp_url)
        wp = xmlrpclib.ServerProxy(wp_url, use_datetime=True)
        blogs = wp.wp.getUsersBlogs(username, password)
        
        notify("Got %d blogs" % len(blogs))
        
        active_blogs = []
        if len(blogs) > 1 and not options.get("all_blogs"):
            notify("Please enter the number of the blog you'd like to import:")
            counter = 1
            for blog in blogs:
                notify("[%d]: %s (ID:%s) " % (counter, blog["blogName"], blog["blogid"]))
                counter+=1
            notify("[a]: All blogs")
            choice = raw_input("Enter %s or 'a' for all blogs" % str(range(1,len(blogs)))).strip()
            if choice.lower() == 'a':
                notify("Grabbing all blogs from this user")
                active_blogs = blogs
            elif int(choice) in range(1,counter):
                notify("Grabbing blog %s" % choice)
                # print blogs
                # print blogs[0]
                # print blogs[1]
                # print '---'
                # print int(choice)-1
                # print blogs[0]
                active_blogs = blogs[int(choice)-1:int(choice)]
        else:
            active_blogs = blogs
        notify("Importing:")
        notify( ",".join(["'%s'" % blog['blogName'] for blog in active_blogs]))
        
        xblog = Blog.objects.get(id=int(xblog_id))
        xblog_author = Author.objects.all()[0] # FIXME: should probably try to get fancy and match email address or some'n
        categories = []
        posts = []
                
        for blog in active_blogs:
            # create a dictionary of categories
            categories = categories + wp.wp.getCategories(blog['blogid'], username, password)
            # create a list of posts
            notify("%d categories" % len(categories))
            # walk through the posts
            filter = {}
            filter['offset'] = 0
            all_posts = []
            counter = 0
            while True:
                filter['number'] = 10
                posts = wp.wp.getPosts(blog['blogid'], username, password, filter)
                # print "%d posts" % len(posts)
                if len(posts) == 0:
                    notify("Done!")
                    break
                for post in posts:
                    # convert the post date. 
                    all_posts.append(post)
                    counter = counter + 1
                    # print "[%3d] %s (%s) %s" % (counter, post['post_title'], post['post_date'], post['post_status']),
                    notify("Title: %s" % post['post_title'])
                    notify("Date: %s" % post['post_date'])
                    notify("Status: %s" % post['post_status'])
                    notify("Author: %s" % post['post_author'])
                    notify("Type: %s" % post['post_type'])
                    notify(10 * "-")
                    # print post['post_content'] 
                filter['offset']+=len(posts)
            
            notify("Downloaded %d posts" % len(all_posts))


            category_map = {}
            for category in categories:
                category_map[category['categoryId']] = self.get_or_create_category(category, xblog)
                
            for post in all_posts:
                pprint( post)
                categories = self.get_post_categories(post, xblog)
                
                # FIXME: start here :-)
                # post['title'] =         post_title
                # post['pub_date'] =      
                # post['update_date'] = 
                # post['create_date'] = 
                # post['enable_comments'] =
                # post['categories'] = categories
                # post['author'] = xblog_author
                
                
                # categories = post['']
                # xblog_category = category_map
            
    def get_or_create_xblog(self, xblog_id):
        # looks for a blog matching either the
        xblog = Blog.objects.get(id=xblog_id)
        return xblog
    
    def get_or_create_category(self, category, xblog):
        # looks for a category in XBlog, creates if it hasn't found one
        # print category
        # slug = self.get_category_slug(category)
        cat = {}
        try:
            xblog_category = Category.objects.get(title=category['description'])
        except ObjectDoesNotExist, e:
            cat['title'] = category['description']
            cat['description'] = category['categoryDescription']
            cat['blog'] = xblog
            
            xblog_category = Category(**cat)
            xblog_category.save()
        return xblog_category
        
    def get_category_slug(self, category):
        # takes a wordpress category, and gets the slug from it
        html_url = category['htmlUrl']
        slug = html_url.split("/category/")[-1]
        slug = slug.replace("/",'')
        return slug
    
    def get_post_categories(self, post, xblog):
        # returns a list of categories for the given post
        category_list = []
        for term in  post['terms']:
            if term['taxonomy'] == 'category':
                mycat = {'description':term['name']}
                category_list.append(self.get_or_create_category(mycat, xblog))
        print category_list
        return category_list


    def get_xmlrpc_url(self, page):
        """
        Gets the API endpoint as encoded in the blog's headers
        """
        print "Opening %s..." % page
        data = urllib.urlopen(page).read()
        print "Got %d bytes" % len(data)
        soup = BeautifulSoup.BeautifulSoup(data)
        xmlrpc_url = [link.get('href') for link in soup.findAll("link", rel="EditURI", type="application/rsd+xml")]
        if len(xmlrpc_url):
            # for now, just return the first one choose a proper link
            return xmlrpc_url[0]
        else:
            return None
        
    def get_posts(self, blog):
        # gets the posts for a particular remote blog 
        pass




def date_to_str(post):
    # print post.keys()
    #post = p.copy()
    for key in post.keys():
        # if it's a dict, recurse
        if type(post[key])==type({}):
            post[key] = date_to_str(post[key])
            
        if key in date_fields:
            # print dir(post[key])
            post[key] = str(post[key].isoformat())
            print "* %s:%s (%s)" % (key, post[key], type(post[key]))
        else:
            print "- |%s| not in date_fields" % key
    
    for key in post.keys():
        print "- %s:%s (%s)" % (key, post[key], type(post[key]))
        # if type(post[k]) != type(''):
        #     print "Non-string: %s\t%s" % (k, type(post[k]))
    
    pprint( post)
    
    return post

def get_urls(post):
    """docstring for get_urls"""
    # this is going to return a list of URLs in the post
    # print post.keys()
    # print post['post_format']

    data = post['post_content']
    # print data
    soup = BeautifulSoup.BeautifulSoup(data)
    urls = {}
    urls['links'] = soup.findAll("a")
    urls['imgs'] = soup.findAll("img")
    return urls

if __name__ == '__main__':
    if sys.argv[-1][-4:]=="json":
        # passed a json file, why not...
        data = json.load(open(sys.argv[-1]))
    else:
    # get a list of posts
        blogs = wp.wp.getUsersBlogs(username, password)
        # list of dicts:
        # [{'url': 'https://subcriticalorg.wordpress.com/', 
        # 'isAdmin': True, 
        # 'blogid': '56586856', 
        # 'xmlrpc': 'https://subcriticalorg.wordpress.com/xmlrpc.php', 
        # 'blogName': 'Subcritical'}, 
        # {'url': 'https://cloudcritical.wordpress.com/', 
        # 'isAdmin': True, 
        # 'blogid': '65316393', 
        # 'xmlrpc': 'https://cloudcritical.wordpress.com/xmlrpc.php', 
        # 'blogName': 'Cloudcritical'}]

        # walk through the blogs...
        print "Got %d blogs" % len(blogs)



        for blog in blogs:
            print "Blog:", blog.get('blogName')
            categories =  wp.wp.getCategories(blog['blogid'], username, password)
            print "%d Categories" % len(categories)
            for category in categories:
                print "- %s [%s][%s]" % (category['categoryName'], category['htmlUrl'], category['categoryId'])
            filter = {}
            # if INCLUDE_DRAFTS:
            #     filter
            filter['offset'] = 0
            all_posts = []
            counter = 0
            while True:

                filter['number'] = 10
                posts = wp.wp.getPosts(blog['blogid'], username, password, filter)
                # print "%d posts" % len(posts)
                if len(posts) == 0:
                    print "Done!"
                    break
                for post in posts:
                    # convert the post date. 
                    all_posts.append(post)
                    counter = counter + 1
                    # print "[%3d] %s (%s) %s" % (counter, post['post_title'], post['post_date'], post['post_status']),
                    print "Title:", post['post_title']
                    print "Date:", post['post_date']
                    print "Status:", post['post_status']
                    print "Author", post['post_author']
                    print "Type:", post['post_type']
                    print 10 * "-"
                    # print post['post_content'] 
                filter['offset']+=len(posts)
        
        # dump posts to json file...
        # print all_posts[-1]
        
        print "Dumping to wp_data.json"
        data = [date_to_str(p) for p in all_posts]
        json.dump(date, open("wp_data.json", 'w'))


    for post in data:
        links = get_urls(post)
        print post['post_title']
        pprint(links)
"""
Importing from a WordPress blog:

- get a list of authors
- get a list of categories
- get a list of posts

First, Create a local cache of all the posts.



map an author to the logged-in guy

"""
import sys
import xmlrpclib
import getpass
import os
import BeautifulSoup
import json
from pprint import pprint
username = "subcriticalorg"
# password = getpass.getpass()
password = open(os.path.expanduser("~/pw.txt")).read().strip()
wp_url = "https://subcriticalorg.wordpress.com/xmlrpc.php"


wp = xmlrpclib.ServerProxy(wp_url, use_datetime=True)

# create all the categories
INCLUDE_DRAFTS=1
# create ALL the posts

date_fields = [ 'date_created',
                'date_created_gmt', 
                'post_date_gmt', 
                'post_date', 
                'post_date_gmt',
                'post_modified',
                'post_modified_gmt']




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
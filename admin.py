from django.contrib import admin
from xblog.models import LinkCategory, Link, Pingback, Tag, Author, Category, Post, Blog
from xblog.models import STATUS_CHOICES, FILTER_CHOICES

class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title',]
admin.site.register(LinkCategory, LinkCategoryAdmin)

class LinkAdmin(admin.ModelAdmin):
    list_display = ('url', 'description')
admin.site.register(Link, LinkAdmin)

class PingbackAdmin(admin.ModelAdmin):
    # list_display = ('pub_date', 'title', 'source_url','target_url')
    search_fields = ('title','pub_date',)
    list_filter = ['pub_date', 'is_public']
admin.site.register(Pingback, PingbackAdmin)

class TagAdmin(admin.ModelAdmin):

    list_display = ('title',)
    search_fields = ('title',)
admin.site.register(Tag, TagAdmin)

class AuthorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Author, AuthorAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','blog')
    search_fields = ('title',)
admin.site.register(Category, CategoryAdmin)

class PostAdmin(admin.ModelAdmin):
    # list_display = ('title',)
    list_display = ('title','pub_date') #,'author','status')
    search_fields = ('title','body','slug')
    date_hierarchy = 'pub_date'
    list_filter = ['author','pub_date', 'status', 'tags', 'categories']
    
    
    
    fieldsets = (
      (None, {'fields':('title','slug',)}),
      ('Date & Time',{'fields':("pub_date","update_date", "create_date")}),
      (None, {'fields':('text_filter','body',)}),
      ('Metadata', {'fields':(
                    'tags',
                    'categories',
                    'blog',
                    'author',
                    'status',
                    'enable_comments')}),
      ('Extras', {'fields':(
                    'summary',
                    'primary_category_name', ), 'classes':'collapse'}),
    )
    
    prepopulated_fields = {"slug": ("title",)}
    radio_fields = {"status":admin.VERTICAL, 
                    "text_filter":admin.VERTICAL}
                    
    readonly_fields = ("update_date", "create_date")
admin.site.register(Post, PostAdmin)

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','owner')
    search_fields = ('title',)
admin.site.register(Blog, BlogAdmin)


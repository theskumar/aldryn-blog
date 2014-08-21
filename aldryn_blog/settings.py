from django.conf import settings


HIDE_ARCHIVE_MENU = getattr(settings, 'ALDRYN_BLOG_HIDE_ARCHIVE_MENU', False)
HIDE_CATEGORIES_MENU = getattr(settings, 'ALDRYN_BLOG_HIDE_CATEGORIES_MENU', False)
HIDE_TAGS_MENU = getattr(settings, 'ALDRYN_BLOG_HIDE_TAGS_MENU', False)
HIDE_AUTHORS_MENU = getattr(settings, 'ALDRYN_BLOG_HIDE_AUTHORS_MENU', False)

APP_URLS = getattr(settings, 'ALDRYN_BLOG_APP_URLS', ['aldryn_blog.urls'])

APP_MENUS = getattr(settings, 'ALDRYN_BLOG_APP_MENUS',
                    ['aldryn_blog.menu.BlogArchiveMenu',
                     'aldryn_blog.menu.BlogCategoriesMenu',
                     'aldryn_blog.menu.BlogTagsMenu',
                     'aldryn_blog.menu.BlogAuthorsMenu'])

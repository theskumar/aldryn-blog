# -*- coding: utf-8 -*-
import warnings

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from aldryn_blog.settings import APP_URLS, APP_MENUS


app_menus = []
for menu_string in APP_MENUS:
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        app_menus.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)


class BlogApp(CMSApp):
    name = _('Blog')
    urls = APP_URLS
    menus = app_menus
    app_name = 'aldryn_blog'

apphook_pool.register(BlogApp)

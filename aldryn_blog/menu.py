from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, get_language_from_request
from django.template.defaultfilters import date as _date
from django.db.models.signals import post_save, post_delete

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode, Modifier
from menus.menu_pool import menu_pool
from aldryn_blog.models import Post, TaggedUnicodeItem
from aldryn_blog.settings import HIDE_ARCHIVE_MENU, HIDE_CATEGORIES_MENU, HIDE_TAGS_MENU, HIDE_AUTHORS_MENU
from aldryn_blog.utils import generate_slugs, get_blog_authors


class BlogTagsMenu(CMSAttachMenu):
    name = _("Blog Tags Menu")

    def get_nodes(self, request):
        nodes = []
        tag_menu_id = 'blog-tag-list'
        attributes = {'hidden': HIDE_TAGS_MENU}
        nodes.append(NavigationNode(
            _('Tags'),
            reverse(
                'aldryn_blog:tag-list'
            ),
            tag_menu_id,
            attr=attributes
        ))
        posts = Post.published.filter_by_current_language()
        tags = TaggedUnicodeItem.objects.none()
        for post in posts:
            tags = tags | TaggedUnicodeItem.tags_for(Post, post).order_by("name")
        for tag in tags:
            node = NavigationNode(
                tag.name,
                reverse(
                    'aldryn_blog:tagged-posts',
                    kwargs={'tag': tag.slug}
                ),
                tag.pk,
                tag_menu_id,
                attr=attributes
            )
            nodes.append(node)
        return nodes


class BlogArchiveMenu(CMSAttachMenu):
    name = _("Blog Entries Menu")

    def get_nodes(self, request):
        nodes = []
        archives = []
        archive_menu_id = 'blog-archive'
        attributes = {'hidden': HIDE_ARCHIVE_MENU}
        nodes.append(NavigationNode(
            _('Archive'),
            reverse(
                'aldryn_blog:latest-posts'
            ),
            archive_menu_id,
            attr=attributes
        ))

        posts = Post.published.filter_by_current_language()
        for post in posts:
            year = post.publication_start.strftime('%Y')
            month = post.publication_start.strftime('%m')
            month_text = _date(post.publication_start, 'F')
            day = post.publication_start.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)
            key_archive_day = 'day-%s-%s-%s' % (year, month, day)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year,
                    reverse(
                        'aldryn_blog:archive-year',
                        kwargs={
                            'year': year
                        }
                    ),
                    key_archive_year,
                    archive_menu_id,
                    attr=attributes)
                )
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse(
                        'aldryn_blog:archive-month',
                        kwargs={
                            'year': year,
                            'month': month
                        }
                    ),
                    key_archive_month,
                    key_archive_year,
                    attr=attributes)
                )
                archives.append(key_archive_month)

            if not key_archive_day in archives:
                nodes.append(NavigationNode(
                    day,
                    reverse(
                        'aldryn_blog:archive-day',
                        kwargs={
                            'year': year,
                            'month': month,
                            'day': day
                        }
                    ),
                    key_archive_day,
                    key_archive_month,
                    attr=attributes)
                )
                archives.append(key_archive_day)

            nodes.append(NavigationNode(
                post.title,
                # post.get_absolute_url(),
                reverse(
                    'aldryn_blog:post-detail',
                    kwargs={
                        'year': year,
                        'month': month,
                        'day': day,
                        'slug': post.slug
                    }
                ),
                post.pk,
                key_archive_day,
                attr=attributes
            ))
        return nodes


class BlogCategoriesMenu(CMSAttachMenu):
    name = _("Blog Categories Menu")

    def get_nodes(self, request):
        nodes = []
        attributes = {'hidden': HIDE_CATEGORIES_MENU}
        categories_menu_id = 'blog-categories'
        nodes.append(NavigationNode(
            _('Categories'),
            reverse(
                'aldryn_blog:category-list'
            ),
            categories_menu_id,
            attr=attributes
        ))

        language = get_language_from_request(request)
        categories = Post.published.get_categories(language)
        for category in categories:
            category_name = category.lazy_translation_getter('name')
            category_slug = category.lazy_translation_getter('slug')
            category_key = 'blog-category-%s' % category_slug

            nodes.append(NavigationNode(
                category_name,
                reverse(
                    'aldryn_blog:category-posts',
                    kwargs={
                        'category': category_slug,
                    }
                ),
                category_key,
                categories_menu_id,
                attr=attributes
            ))

        return nodes


class BlogAuthorsMenu(CMSAttachMenu):
    name = _("Blog Authors Menu")

    def get_nodes(self, request):
        nodes = []
        attributes = {'hidden': HIDE_AUTHORS_MENU}
        authors_menu_id = 'blog-authors'
        nodes.append(NavigationNode(
            _('Authors'),
            reverse(
                'aldryn_blog:author-list'
            ),
            authors_menu_id,
            attr=attributes
        ))

        authors = generate_slugs(get_blog_authors())
        for author in authors:
            author_name = author.get_full_name()
            author_slug = author.slug
            author_key = 'blog-author-%s' % author_slug

            nodes.append(NavigationNode(
                author_name,
                reverse(
                    'aldryn_blog:author-posts',
                    kwargs={
                        'slug': author_slug,
                    }
                ),
                author_key,
                authors_menu_id,
                attr=attributes
            ))

        return nodes


# It's from Zinnia
# https://github.com/Fantomas42/cmsplugin-zinnia/blob/develop/cmsplugin_zinnia/menu.py#L116
class BlogEntryModifier(Modifier):
    """Menu Modifier for entries,
    hide the MenuEntry in navigation, not in breadcrumbs"""

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """Modify nodes of a menu"""
        if breadcrumb:
            return nodes
        for node in nodes:
            if node.attr.get('hidden'):
                node.visible = False
        return nodes

menu_pool.register_menu(BlogTagsMenu)
menu_pool.register_menu(BlogArchiveMenu)
menu_pool.register_menu(BlogCategoriesMenu)
menu_pool.register_menu(BlogAuthorsMenu)
menu_pool.register_modifier(BlogEntryModifier)

def invalidate_menu_cache(sender, **kwargs):
    """
    Signal receiver to invalidate the menu_pool
    cache when an entry is posted
    """
    menu_pool.clear()

post_save.connect(
    invalidate_menu_cache, sender=Post,
    dispatch_uid='aldryn_blog.post.postsave.invalidate_menu_cache')
post_delete.connect(
    invalidate_menu_cache, sender=Post,
    dispatch_uid='aldryn_blog.post.postdelete.invalidate_menu_cache')

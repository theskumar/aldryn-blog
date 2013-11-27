from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode, Modifier
from menus.menu_pool import menu_pool
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django.template.defaultfilters import date as _date
from aldryn_blog.models import Post, TaggedUnicodeItem


class BlogTagsMenu(CMSAttachMenu):
    name = _("Blog Tags Menu")

    def get_nodes(self, request):
        nodes = []
        posts = Post.published.filter_by_current_language()
        tags = TaggedUnicodeItem.objects.none()
        for post in posts:
            tags = tags | TaggedUnicodeItem.tags_for(Post, post).order_by("name")
        for tag in tags:
            node = NavigationNode(
                tag.name,
                reverse(
                    'aldryn_blog:tagged-posts', kwargs={'tag': tag.slug}),
                tag.pk
            )
            nodes.append(node)
        return nodes


class BlogEntriesMenu(CMSAttachMenu):
    name = _("Blog Entries Menu")

    def get_nodes(self, request):
        nodes = []
        archives = []
        posts = Post.published.filter_by_current_language()
        attributes = {'hidden': True}
        for post in posts:
            year = post.publication_start.strftime('%Y')
            month = post.publication_start.strftime('%m')
            month_text = _date(post.publication_start, 'F')
            day = post.publication_start.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year, reverse('aldryn_blog:archive-year', args=[year]),
                    key_archive_year, attr=attributes))
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse('aldryn_blog:archive-month', args=[year, month]),
                    key_archive_month, key_archive_year,
                    attr=attributes))
                archives.append(key_archive_month)

            nodes.append(NavigationNode(
                post.title,
                reverse(
                    'aldryn_blog:post-detail', kwargs={
                        'year': year,
                        'month': month,
                        'day': day,
                        'slug': post.slug
                    }),
                post.pk,
                attr=attributes
            ))
        return nodes


# It's from Zinnia
# https://github.com/Fantomas42/cmsplugin-zinnia/blob/develop/cmsplugin_zinnia/menu.py#L116
class EntryModifier(Modifier):
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
menu_pool.register_menu(BlogEntriesMenu)
menu_pool.register_modifier(EntryModifier)

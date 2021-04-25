from django import template
from bbs import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


@register.inclusion_tag('left.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 1.查询当前用户的站点所有的分类以及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list(
        'name', 'count_num', 'pk')
    # 2.查询当前用户所有的标签以及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list(
        'name', 'count_num', 'pk')
    # 3.日期的分组查询
    month_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month')\
        .annotate(article_num=Count('pk')).values_list('month', 'article_num')
    return locals()

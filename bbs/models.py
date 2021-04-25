from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# 继承user表要去settings中声明：AUTH_USER_MODEL = '应用名.UserInfo'
class UserInfo(AbstractUser):
    is_deleted = models.BooleanField(default=False)  # 如果该用户选择销号，把这个字段改成True
    avatar = models.FileField(upload_to='avatar/', default='/static/img/default.png')
    # 外键字段blog
    blog = models.OneToOneField(to='Blog', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户信息表'


class Blog(models.Model):
    title = models.CharField(max_length=32, verbose_name='站点标题')
    name = models.CharField(max_length=32, verbose_name='站点名称')
    style = models.CharField(max_length=32, verbose_name='站点样式', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '用户个人站点'


class Article(models.Model):
    title = models.CharField(max_length=32, verbose_name='文章标题')
    desc = models.CharField(max_length=32, verbose_name='文章摘要', null=True, blank=True)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True)
    # 优化字段
    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    # 外键字段，与用户表/个人站点表一对多，文章表是多的一方，建立外键
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)  # 一对多，外键字段建在多的一方
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, null=True)  # 一对一，建在查询频率高一方
    tag = models.ManyToManyField(to='Tag')  # 多对多，自动建立第三张表

    def __str__(self):
        try:
            return self.title + '-----' + self.blog.title
        except:
            return self.title

    class Meta:
        verbose_name_plural = '文章详情表'


class UpAndDown(models.Model):
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    article_id = models.ForeignKey(to=Article, on_delete=models.CASCADE)
    is_up = models.BooleanField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '点赞点踩表'


class Comment(models.Model):
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    article_id = models.ForeignKey(to=Article, on_delete=models.CASCADE)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    comment_id = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = '评论表'


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='标签名称')
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + '-----' + self.blog.title

    class Meta:
        verbose_name_plural = '个人站点标签表'


class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='分类名称')
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + '-----' + self.blog.title

    class Meta:
        verbose_name_plural = '个人站点分类表'

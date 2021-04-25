"""BBSupdate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from bbs import views
from django.views.static import serve
from BBSupdate import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register),
    path('login/', views.login),
    path('verify_code/', views.verify_code),
    path('index/', views.index),
    # index登录后可以修改密码
    path('set_password/', views.set_password),
    # index登录后可以修改头像
    path('change_avatar/', views.change_avatar),
    # index登录后可以注销用户
    path('set_delete/', views.set_delete),
    path('logout/', views.logout),
    # 注册页面用户名输入后判断用户名是否被注册
    path('dynamic/', views.dynamic),
    path('up_and_down/', views.up_and_down),
    path('comment/', views.comment),
    # 后台管理
    path('backend/', views.backend),
    # path('edit/', views.edit),
    # path('delete/', views.delete),
    # 新建文章
    path('add_article/', views.add_article),
    # 上传图片
    path('upload_img/', views.upload_img),
    re_path('^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

    # 个人页面的搭建
    re_path(r'^(?P<username>\w+)/$', views.site, name='site'),
    # 个人页面侧边栏可选功能
    re_path(r'^(?P<username>\w+)/(?P<option>category|tag|archive)/(?P<name>.*)', views.site, name='site'),
    # 文章详情
    re_path(r'^(?P<username>\w+)/article/(?P<article_id>\d+)', views.article_detail),
]

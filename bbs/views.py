import json
import random
import os
import time
import threading
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bbs import models
from bbs import my_reg_form
from BBSupdate import settings
from static.utils.paper import Pagination


# Create your views here.
def register(request):
    form = my_reg_form.RegForm()
    if request.method == 'POST':
        response = {'status': 100, 'msg': None}
        form = my_reg_form.RegForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            file = request.FILES.get('myfile')
            if file:
                clean_data['avatar'] = file
            clean_data.pop('re_password')
            models.UserInfo.objects.create_user(**clean_data)
            response['msg'] = '恭喜您，完成注册'
            response['url'] = '/login/'
        else:
            response['status'] = 101
            response['msg'] = form.errors
        return JsonResponse(response)
    elif request.method == 'GET':
        return render(request, 'register.html', locals())


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def verify_code(request):
    img = Image.new('RGB', (250, 30), (250, 250, 250))
    img_font = ImageFont.truetype('./static/font/ss.TTF', 25)
    img_draw = ImageDraw.Draw(img)
    v_code = ''
    for i in range(5):
        lower_letter = chr(random.randint(65, 90))
        upper_letter = chr(random.randint(97, 122))
        num = str(random.randint(0, 9))
        one = random.choice([lower_letter, upper_letter, num])
        v_code += one
        img_draw.text((20 + i * 40, 0), one, fill=get_random(), font=img_font)
    print(v_code)
    request.session['code'] = v_code
    width = 250
    height = 30
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        img_draw.line((x1, y1, x2, y2), fill=get_random())
    for i in range(20):
        img_draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random())
        x = random.randint(0, width)
        y = random.randint(0, height)
        img_draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random())
    bytes_io = BytesIO()
    img.save(bytes_io, 'png')
    return HttpResponse(bytes_io.getvalue())


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', locals())
    else:
        response = {'status': 100, 'msg': None}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if code.upper() == request.session.get('code').upper():
            username_verify = models.UserInfo.objects.filter(username=username)
            user = auth.authenticate(username=username, password=password)
            if username_verify.first().is_deleted:
                response['msg'] = '用户名不存在'
                response['status'] = 103
                return JsonResponse(response)
            if user:
                auth.login(request, user)
                response['msg'] = '登陆成功'
                response['url'] = '/index/'
            else:
                if not username_verify:
                    response['msg'] = '用户名不存在'
                    response['status'] = 103
                else:
                    response['msg'] = '密码错误'
                    response['status'] = 102
        else:
            response['msg'] = '验证码错误'
            response['status'] = 101
        return JsonResponse(response)


def index(request):
    if request.user.is_authenticated:
        user_avatar = models.UserInfo.objects.filter(username=request.user.username).first()
    banner_list = [{
        'name': 'welcome',
        'url': '/static/img/banner/banner1.jpeg',
    }, {
        'name': 'bbs',
        'url': '/static/img/banner/banner2.jpeg',
    }, {
        'name': 'index',
        'url': '/static/img/banner/banner3.jpeg',
    }]
    current_page = request.GET.get('page', 1)
    article_list = models.Article.objects.all()
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'index.html', locals())


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/index/')


@login_required
def set_password(request):
    response = {'status': 100, 'msg': None}
    if request.is_ajax():
        password = request.POST.get('password')
        old_password = request.POST.get('old_password')
        res = request.user.check_password(old_password)
        if res:  # 如果校验旧密码成功
            request.user.set_password(password)
            request.user.save()
            response['msg'] = '密码修改成功'
            response['url'] = '/login/'
        else:  # 校验旧密码失败
            response['status'] = 101
            response['msg'] = '旧密码输入错误'
        return JsonResponse(response)


@login_required
def change_avatar(request):
    user_avatar = models.UserInfo.objects.filter(username=request.user.username).first()
    if request.is_ajax():
        user_obj = request.user
        my_avatar = request.FILES.get('myfile')
        print(my_avatar, type(my_avatar))
        user_obj.avatar = my_avatar
        user_obj.save()
        return redirect('/index/')
    return render(request, 'change_avatar.html', locals())


@login_required
def set_delete(request):
    response = {'status': 100, 'msg': None}
    if request.user.is_authenticated and request.is_ajax():
        user_obj = request.user
        user_obj.is_deleted = True
        user_obj.save()
        response['url'] = '/login/'
        return JsonResponse(response)


def dynamic(request):
    response = {'status': 100, 'msg': None}
    if request.is_ajax():
        username = request.POST.get('username')
        obj = models.UserInfo.objects.filter(username=username)
        if obj:
            response['msg'] = f'用户名{username}已被注册过'
        return JsonResponse(response)


def site(request, username, **kwargs):
    if request.user.is_authenticated:
        user_avatar = models.UserInfo.objects.filter(username=request.user.username).first()
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'errors.html')
    blog = user_obj.blog
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:  # 如果有额外参数说明再进行一次筛选
        option = kwargs['option']
        if option == 'category':  # 进入目录分组
            article_list = article_list.filter(category_id=int(kwargs['name'].strip('/')))
        elif option == 'tag':  # 进入标签分组
            article_list = article_list.filter(tag__id=int(kwargs['name'].strip('/')))
        elif option == 'archive':  # 进入日期归档
            year, month = kwargs['name'].strip('/').split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
        else:  # 如果option什么也没有匹配到
            return render(request, 'errors.html')
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    if request.user.is_authenticated:
        user_avatar = models.UserInfo.objects.filter(username=request.user.username).first()
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(id=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'errors.html')
    comment_list = models.Comment.objects.filter(article_id=article_id)
    return render(request, 'article_detail.html', locals())


def up_and_down(request):
    response = {'status': 100, 'msg': None}
    if request.is_ajax():
        user_id = models.UserInfo.objects.filter(username=request.user.username).first()
        article_id = models.Article.objects.filter(pk=request.POST.get('article_id')).first()
        is_up = json.loads(request.POST.get('is_up'))
        if not request.user.is_authenticated:
            response['status'] = 101
            response['msg'] = '请先<a href="/login/">登录</a>'
            return JsonResponse(response)
        up_or_down = models.UpAndDown.objects.filter(user=user_id, article_id=article_id).first()
        if up_or_down:
            response['status'] = 102
            response['msg'] = '您已点过'
        else:
            # 在表中创建点赞记录
            models.UpAndDown.objects.create(user=user_id, article_id=article_id, is_up=is_up)
            if is_up:  # 如果点了赞，对article表中点赞优化字段+1
                models.Article.objects.filter(pk=request.POST.get('article_id')).update(up_num=F('up_num')+1)
                response['msg'] = '已成功点赞'
            else:
                models.Article.objects.filter(pk=request.POST.get('article_id')).update(down_num=F('down_num')+1)
                response['msg'] = '已成功点踩'
        return JsonResponse(response)


def comment(request):
    response = {'status': 100, 'msg': None}
    if request.is_ajax():
        user = request.user
        article_id = request.POST.get('article_id')
        comment_content = request.POST.get('comment')
        comment_id = request.POST.get('parent_id')
        res = models.Comment.objects.create(user=user, article_id_id=article_id, content=comment_content, comment_id_id=comment_id)
        models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num')+1)
        response['username'] = request.user.username
        if comment_id:
            response['status'] = 101
            response['parent'] = models.UserInfo.objects.filter(pk=comment_id).first().username
            response['parent_comment'] = res.comment_id.content  # 因为是根评论所以需要绕一下才能拿到
        # 可以对评论内容进行一些校验，校验完成后，把content重新放入response
        response['content'] = res.content
        """ 如果需要给作者发送邮件需要去settings中配置，然后回来发送邮件
        因为发送邮件是同步发送，会比较慢，可以开一个线程异步发送
        t = threading.Thread(target=send_mail, args=(f"您的文章{article_id}新增了一条评论", f'{comment_content}',
                                                     settings.EMAIL_HOST_USER, ["776163160@qq.com"]))
        t.start()
        """
        return JsonResponse(response)


@login_required
def backend(request):
    if request.user.is_authenticated:
        user_avatar = models.UserInfo.objects.filter(username=request.user.username).first()
    article_list = models.Article.objects.all()
    if request.method == 'GET':
        return render(request, 'backend/backend_index.html', locals())


@login_required
def add_article(request):
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    category_list = models.Category.objects.filter(blog=request.user.blog)
    if request.method == 'GET':
        return render(request, 'backend/add_article.html', locals())
    else:
        title = request.POST.get('article_title')
        content = request.POST.get('article_content')
        tag = request.POST.getlist('article_tag')
        category = request.POST.get('optionsRadios article_category')
        # 第一个参数是要解析的html文档内容
        # 第二个参数是使用的解析器（html.parser和lxml）
        soup = BeautifulSoup(content, 'html.parser')
        desc = soup.text[:250]
        script_list = soup.find_all('script')
        for script in script_list:
            script.decompose()  # 把当前标签对象，从文档中删除
        article = models.Article.objects.create(title=title, desc=desc, content=str(soup),
                                                blog=request.user.blog, category_id=category)
        article.add(tag)
    return redirect('/backend/')


@csrf_exempt
def upload_img(request):
    print(request.FILES)
    try:
        file = request.FILES.get('imgFile')
        file_name = str(time.time()) + file.name
        path = os.path.join(settings.MEDIA_ROOT, 'img', file_name)
        with open(path, 'wb') as f:
            for line in file:
                f.write(line)
        return JsonResponse({"error": 0, "url": '/media/img/' + file_name})
    except Exception as e:
        return JsonResponse({"error": 1, "message": str(e)})
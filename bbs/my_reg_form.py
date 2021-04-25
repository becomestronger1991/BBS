from django import forms
from django.forms import widgets
from bbs.models import UserInfo
from django.core.exceptions import ValidationError


class RegForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=2, label='用户名',
                               error_messages={
                                   'required': '用户名项必填',
                                   'max_length': '用户名不能长于20个字符',
                                   'min_length': '用户名不能少于2个字符', },
                               widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=20, min_length=8, label='密码',
                               error_messages={
                                   'required': '密码项必填',
                                   'min_length': '密码不能少于8个字符',
                                   'max_length': '密码不能长于20个字符', },
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=20, min_length=8, label='确认密码',
                                  error_messages={
                                      'required': '确认密码项必填',
                                      'min_length': '确认密码不能少于8个字符',
                                      'max_length': '确认密码不能长于20个字符', },
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='用户邮箱', error_messages={
        'required': '邮箱必填',
        'invalid': '邮箱格式不正确', },
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_obj = UserInfo.objects.filter(username=username).first()
        if user_obj:
            raise ValidationError(f'用户名{username}已被注册，请重新填写')
        return username

from django.forms import ModelForm
from captcha.fields import CaptchaField

from .models import Post, Comment


class PostForm(ModelForm):
    '''
    Форма для создания и редактирования постов
    '''
    class Meta:
        model = Post
        fields = ['text', 'group', 'image',]


class CommentForm(ModelForm):
    '''
    Форма для создания комментариев
    '''
    captcha = CaptchaField()
    class Meta:
        model = Comment
        fields = ['text', 'captcha']

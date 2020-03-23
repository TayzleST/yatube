from django.forms import ModelForm
from captcha.fields import CaptchaField
from django.conf import settings

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
    # включение/отключение капчи
    if not settings.DISABLE_CAPTCHA:
        captcha = CaptchaField()
    class Meta:
        model = Comment
        fields = ['text',]

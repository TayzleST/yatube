from django.forms import ModelForm

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
    class Meta:
        model = Comment
        fields = ['text',]

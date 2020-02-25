from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    '''
    Модель групп пользователей
    '''
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    '''
    Модель постов пользователей
    '''
    text = models.TextField(verbose_name='текст')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_author")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, verbose_name='группа')
    image = models.ImageField(upload_to='posts/', blank=True,)

    def __str__(self):
        return self.text



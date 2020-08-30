from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_file_size


User = get_user_model()


class Group(models.Model):
    """
    Модель групп пользователей
    """

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Модель постов пользователей
    """

    text = models.TextField(verbose_name="текст")
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_author"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="группа",
    )
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        validators=[validate_file_size],
        verbose_name="изображение",
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    """
    Модель комментариев пользователей
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comment_post",
        verbose_name="комментарий",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_author",
        verbose_name="автор комментария",
    )
    text = models.TextField(verbose_name="текст")
    created = models.DateTimeField("created", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """
    Модель подписки на авторов
    """

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )

    class Meta:
        unique_together = ["author", "user"]

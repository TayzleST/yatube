from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token

from django.core.paginator import Paginator

from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm


def index(request):
    # главная страница
    post_list = Post.objects.select_related('author').order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    # все посты выбранной группы
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group', 'author').filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    # Создание нового поста
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm(request.POST or None)
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    # Страница профиля зарегистрированного пользователя.
    # Содержит данные о пользователе и его посты.
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('author').filter(author=profile).order_by("-pub_date").all()
    posts_count = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {'profile': profile, 'posts_count': posts_count,
                                            'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    # Страница просмотра выбранного поста.
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    # добавляем форму для комментирования
    form = CommentForm(request.POST or None)
    # комментарии к посту
    items = Comment.objects.select_related('post').filter(post=post)
    # проверка на соответствие id поста выбранному автору
    if post.author == profile:
        posts_count = Post.objects.select_related('author').filter(author=profile).count()
        return render(request, "post.html", {'profile': profile, 'post': post,
                                'posts_count': posts_count, 'items': items, 'form': form})
    return redirect('profile', username=profile.username)

def post_edit(request, username, post_id):
    # Редактирование поста
    post = get_object_or_404(Post, id=post_id)
    # проверка, что текущий юзер и автор поста совпадают
    if request.user == post.author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post', username=username, post_id=post_id)
        else:
            form = PostForm(instance=post)
        return render(request, 'new_post.html', {'form': form, 'post': post} )
    return redirect('post', username=username, post_id=post_id)


def post_confirm(request, username, post_id):
    # Запрос подтверждения на удаление поста.
    # проверка, что текущий юзер и автор поста совпадают
    if request.user == get_object_or_404(Post, id=post_id).author:
        return render(request, 'confirm.html', {'post_id': post_id, 'username': username} )
    return redirect('post', username=username, post_id=post_id)


def post_delete(request, username, post_id):
    # Удаление поста.
    # проверка, что текущий юзер и автор поста совпадают
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        return redirect('profile', username=username)
    return redirect('post', username=username, post_id=post_id)


# @requires_csrf_token
def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


# @requires_csrf_token
def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    # Получаем пост, для которого будет создан комментарий
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username=username, post_id=post_id)
    else:
        form = CommentForm(request.POST or None)
    items = Comment.objects.filter(post=post)    
    return render(request, 'post.html', {'form': form, 'post': post, 'items': items} )

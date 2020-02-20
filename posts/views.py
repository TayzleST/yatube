from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    # главная страница
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    # все посты выбранной группы
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    # Создание нового поста
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm(request.POST)
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    # Страница профиля зарегистрированного пользователя.
    # Содержит данные о пользователе и его посты.
    profile = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=profile).count()
    post_list = Post.objects.filter(author=profile).order_by("-pub_date").all()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {'profile': profile, 'posts_count': posts_count,
                                            'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    # Страница просмотра выбранного поста.
    profile = User.objects.get(username=username)
    posts_count = Post.objects.filter(author=profile).count()
    # проверка на совпадение id поста с автором поста
    if Post.objects.get(id=post_id).author == profile:
        post = Post.objects.get(id=post_id)
        return render(request, "post.html", {'profile': profile, 'post': post,
                                'posts_count': posts_count})
    return redirect('profile', username=profile.username)

def post_edit(request, username, post_id):
    # Редактирование поста
    # проверка, что текущий юзер и автор поста совпадают
    if request.user == get_object_or_404(Post, id=post_id).author:
        post = get_object_or_404(Post, id=post_id)
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
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
    if request.user == get_object_or_404(Post, id=post_id).author:
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return redirect('profile', username=username)
    return redirect('post', username=username, post_id=post_id)

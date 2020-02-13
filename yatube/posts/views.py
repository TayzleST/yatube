from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.core.paginator import Paginator

from .models import Post, Group
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm(request.POST)
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
        # тут тело функции
        return render(request, "profile.html", {})

def post_view(request, username, post_id):
        # тут тело функции
        return render(request, "post.html", {})

def post_edit(request, username, post_id):
        # тут тело функции. Не забудьте проверить, 
        # что текущий пользователь — это автор записи.
        # В качестве шаблона используйте шаблон для создания новой записи,
        # который вы использовали раньше (вы могли назвать шаблон иначе)
        return render(request, "post_new.html", {}) 


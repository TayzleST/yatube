"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500, url
from django.conf import settings
from django.conf.urls.static import static


handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa


urlpatterns = [
    # импорт правил из приложения admin
    path("admin/", admin.site.urls),
    # flatpages
    path("about/", include("django.contrib.flatpages.urls")),
    # регистрация и авторизация
    path("auth/", include("users.urls")),
    # если нужного шаблона для /auth не нашлось в файле users.urls — 
    # ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),
]
    
    # пути для flatpages
urlpatterns += [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
]
    # пути для flatpages
urlpatterns += [
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='spec'),
    path('contacts/', views.flatpage, {'url': '/contacts/'}, name='contacts'),
]

    # путь для captcha
urlpatterns += [
    url(r'^captcha/', include('captcha.urls')),
]

urlpatterns += [
    # обработчик для главной страницы ищем в urls.py приложения posts
    path("", include("posts.urls")),
]

    # пути для картинок пользователей
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # путь для django-debug-toolbar
if settings.DEBUG:
    import debug_toolbar # pylint: disable=import-error
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
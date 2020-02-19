from django.urls import path
from . import views

urlpatterns = [
    # создание нового поста
    path("new/", views.new_post, name="new_post"),
    # вывод всех постов группы
    path('group/<slug>/', views.group_posts, name='group_posts'),
    # Профайл пользователя
    path("<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    # редактирование выбранного поста
    path("<username>/<int:post_id>/edit", views.post_edit, name="post_edit"),
    # подтверждение удаления выбранного поста
    path("<username>/<int:post_id>/confirm", views.post_confirm, name="post_confirm"),
    # удаление выбранного поста
    path("<username>/<int:post_id>/delete", views.post_delete, name="post_delete"),
    # главная страница со всеми постами всех пользователей
    path('', views.index, name='index'),
]


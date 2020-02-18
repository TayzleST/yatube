from django.urls import path
from . import views

urlpatterns = [
    path("new/", views.new_post, name="new_post"),
    path('group/<slug>/', views.group_posts, name='group_posts'),
    # Профайл пользователя
    path("<username>/", views.profile, name="profile"),
    # Просмотр записи
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("<username>/<int:post_id>/delete", views.post_delete, name="post_delete"),
    path('', views.index, name='index'),
]


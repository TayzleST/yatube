from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("new/", views.new_post, name="new_post"),
    path("<username>/<int:post_id>/", views.view_post, name="post"),
    path('group/<slug>/', views.group_posts, name='group_posts'),
]


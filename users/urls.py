from django.urls import path
from . import views

urlpatterns = [
    # страница регистрации
    path("signup/", views.SignUp.as_view(), name="signup")
]

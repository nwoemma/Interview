from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path("signup/", views.signup, name="signup" ),
    path('signin/', views.signin, name="signin/"),
    path('profile/', views.profile, name="profile")
]
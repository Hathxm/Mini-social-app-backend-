from django.urls import path
from .import views
urlpatterns = [
    path('signup/', views.Signup.as_view(),name="signup-pg"),
    path('login/', views.Login.as_view(),name="Login-pg"),
    path('users/', views.UsersDetails.as_view(),name="users-details"),
    path('user-details/', views.UserDetails.as_view(),name="user-details"),
    path('token/refresh/',views.token_refresh.as_view(),name='token_refresh'),


    # path('', views,name=""),


]

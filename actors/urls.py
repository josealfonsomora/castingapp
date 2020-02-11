"""actors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path

from rest_framework_simplejwt.views import (TokenObtainPairView)
from apps.accounts.serializers import CustomJWTSerializer
from apps.posts.views import (PostResource, PostSingleResource,
                              PostMediaResource, PostMediaSingleResource)
from apps.accounts.views import (CurrentUserProfile, UserRecoverPassword,
                                 UserChangePassword)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', TokenObtainPairView.as_view(serializer_class=CustomJWTSerializer), name='auth_get_token'),
    path('auth/recoverpass/', UserRecoverPassword.as_view(), name='auth_recover_pass'),
    path('auth/changepass/', UserChangePassword.as_view(), name='auth_change_pass'),
    path('auth/profile/', CurrentUserProfile.as_view(), name='auth_change_pass'),
    path('posts/<int:postid>/', PostSingleResource.as_view()),
    path('posts/', PostResource.as_view()),
    path('postmedia/<int:postid>/', PostMediaSingleResource.as_view()),
    path('postmedia/', PostMediaResource.as_view())
]

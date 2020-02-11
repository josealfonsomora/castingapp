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

from apps.accounts.views import EmailTokenObtainPairView
from apps.posts.views import PostResource, PostSingleResource, PostMediaResource, PostMediaSingleResource

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('posts/<int:postid>/', PostSingleResource.as_view()),
    path('posts/', PostResource.as_view()),
    path('postmedia/<int:postid>/', PostMediaSingleResource.as_view()),
    path('postmedia/', PostMediaResource.as_view())
]

"""umoeditor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.urls import path
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
#import django.contrib.auth.views
import problemeditor.views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'),name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'),name='logout'),
#    url(r'^accounts/login/$',django.contrib.auth.views.login, name='login'),
#    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout', kwargs={'next_page': '/'}),
    path('accounts/change-password/', auth_views.PasswordChangeView.as_view(template_name='registration/change-password.html'),name='change_password'),
    path('accounts/change-password-done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/change-password-done.html'),name='password_change_done'),
#    url(r'^accounts/change-password/$', problemeditor.views.UpdatePassword, name='change_password'),
#    url(r'^accounts/change-password-done/$', django.contrib.auth.views.password_change_done, name='password_change_done'),
    url(r'', include('problemeditor.urls')),
    url(r'ratings/', include('star_ratings.urls', namespace='ratings')),
]
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

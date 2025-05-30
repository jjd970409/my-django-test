"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views  # 로그인/로그아웃 뷰 임포트
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from hello.views import CustomLoginView, SignUpView, send_verification_email, validate_field  # SignUpView 추가

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/', permanent=True)),  # 루트 URL을 /login/으로 리다이렉트
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('send-verification-email/', send_verification_email, name='send_verification_email'),
    path('signup/', SignUpView.as_view(), name='signup'),  # 이 라인 추가
    path('validate/<str:field_name>/', validate_field, name='validate_field'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
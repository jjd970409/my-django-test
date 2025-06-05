from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
app_name = 'hello'

urlpatterns = [
    path('', login_required(views.home), name='home'),  # 홈 뷰 추가
]
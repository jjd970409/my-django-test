from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),  # 루트 URL에 hello_world 뷰 연결
    # 메시지 삭제를 위한 URL 패턴 (delete/<id>/)
    path('delete/<int:msg_id>/', views.delete_message, name='delete_message'),
]

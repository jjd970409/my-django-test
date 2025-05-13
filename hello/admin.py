from django.contrib import admin
from .models import Message

# Message 모델을 관리자(admin)에서 관리할 수 있도록 등록
admin.site.register(Message)

# Register your models here.

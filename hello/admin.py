from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Message 모델을 관리자(admin)에서 관리할 수 있도록 등록
admin.site.register(User, UserAdmin)

# Register your models here.

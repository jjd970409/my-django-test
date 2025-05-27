from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    nickname = models.CharField(_('닉네임'), max_length=30, unique=True)
    email_verified = models.BooleanField(_('이메일 인증 여부'), default=False)
    email_verification_code = models.CharField(_('이메일 인증코드'), max_length=6, null=True, blank=True)
    
    def __str__(self):
        return self.username
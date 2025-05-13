from django.db import models

# 메시지를 저장하는 모델
class Message(models.Model):
    content = models.CharField(max_length=100)  # 메시지 내용 필드

    def __str__(self):
        # Admin 등에서 객체를 문자열로 볼 때 표시
        return self.content

# Create your models here.

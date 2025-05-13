from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Message  # Message 모델 임포트
from django.contrib import messages  # Django 메시지 프레임워크 사용
from django.contrib.auth.decorators import login_required  # 로그인 필수 데코레이터

# Create your views here.
# @login_required: 로그인하지 않은 사용자는 자동으로 /login/ 으로 이동
@login_required(login_url='/login/')
def hello_world(request):
    msg_text = ""
    msg_type = ""  # 'success' 또는 'error'
    if request.method == "POST":
        # 폼에서 입력받은 메시지 내용 가져오기 및 공백 제거
        content = request.POST.get("content", "").strip()
        if not content:
            # 입력값이 비어있을 때
            msg_text = "메시지를 입력하세요."
            msg_type = "error"
        elif len(content) > 100:
            # 입력값이 100자 초과일 때
            msg_text = "메시지는 100자 이내로 입력하세요."
            msg_type = "error"
        else:
            # 정상 입력: DB에 새 메시지 저장
            Message.objects.create(content=content)
            # Django messages 프레임워크로 성공 메시지 전달
            messages.success(request, "메시지가 저장되었습니다!")
            return redirect('hello_world')  # PRG 패턴 적용
    # DB에서 모든 메시지 조회
    message_list = Message.objects.all()  # DB 메시지 리스트
    # 템플릿에 message_list, 피드백 메시지 전달
    return render(request, 'hello/hello.html', {
        'message_list': message_list,  # DB 메시지 리스트
        'msg_text': msg_text,
        'msg_type': msg_type,
    })

# 메시지 삭제를 처리하는 뷰
from django.shortcuts import redirect

def delete_message(request, msg_id):
    if request.method == "POST":
        # msg_id에 해당하는 메시지를 DB에서 삭제
        Message.objects.filter(id=msg_id).delete()
    # 삭제 후 메시지 목록 페이지로 리다이렉트
    return redirect('hello_world')

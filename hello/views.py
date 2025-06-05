from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages  # Django 메시지 프레임워크 사용
from django.contrib.auth.decorators import login_required  # 로그인 필수 데코레이터
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import User
import random
import string
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import re

@login_required
def home(request):
    return render(request, 'hello/home.html')  

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """로그인 성공 시 세션 갱신"""
        response = super().form_valid(form)
        if self.request.user.is_authenticated:
            # 세션 갱신
            self.request.session.cycle_key()
        return response

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # 로그인한 사용자는 회원가입 페이지 접근 불가
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        """폼 검증 실패 시 입력값 유지"""
        for field in form.errors:
            form[field].field.widget.attrs['class'] = 'form-control is-invalid'
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        # 인증번호 확인
        user_code = form.cleaned_data.get('email_verification_code')
        session_code = self.request.session.get('verification_code')
        email = form.cleaned_data.get('email')
        
        session_email = self.request.session.get('verification_email')
        if session_email != email:
            form.add_error('email_verification_code', '이메일 인증을 다시 진행해주세요.')
            return self.form_invalid(form)
        
        if user_code != session_code:
            form.add_error('email_verification_code', '인증번호가 일치하지 않습니다.')
            return self.form_invalid(form)
            
        # 유저 저장
        user = form.save(commit=False)
        user.email_verified = True
        user.save()

        # 세션 정리
        if 'verification_code' in self.request.session:
            del self.request.session['verification_code']
        if 'verification_email' in self.request.session:
            del self.request.session['verification_email']
        
        messages.success(self.request, '🎉 회원가입이 완료되었습니다! 로그인해주세요.')
        return super().form_valid(form)

@require_http_methods(["POST"])
@csrf_exempt
def send_verification_email(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': '이메일을 입력해주세요.'}, status=400)
                
            # 이메일 형식 검증
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({'error': '유효한 이메일 주소를 입력해주세요.'}, status=400)
                
            if get_user_model().objects.filter(email=email).exists():
                return JsonResponse({'error': '이미 사용 중인 이메일입니다.'}, status=400)
                
            # 인증번호 생성 (6자리 숫자)
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # 세션에 저장 (5분간 유효)
            request.session['verification_code'] = verification_code
            request.session['verification_email'] = email
            request.session.set_expiry(300)  # 5분 후 만료
            
            # 이메일 전송 (개발용 콘솔 출력)
            print(f"이메일 인증번호 ({email}): {verification_code}")
            
            # 실제 이메일 전송 (실제 배포 시 사용)
            # send_mail(
            #     '[사이트명] 이메일 인증번호',
            #     f'인증번호: {verification_code}',
            #     'noreply@yourdomain.com',
            #     [email],
            #     fail_silently=False,
            # )
            
            return JsonResponse({
                'message': '인증번호가 전송되었습니다.',
                'verification_code': verification_code  # 개발용으로 임시로 코드 반환
            })
            
        except Exception as e:
            return JsonResponse({'error': '서버 오류가 발생했습니다.'}, status=500)
            
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def validate_field(request, field_name):

    print(f"\n=== New Validation Request ===")
    print(f"Request Method: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"Request Body: {request.body}")  # 요청 본문 출력

    try:
        print(f"Validating field: {field_name}")  # 디버깅용 로그
        data = json.loads(request.body)
        value = data.get('value', '').strip()
        response_data = {'valid': True, 'message': ''}
        User = get_user_model()  # User 모델 미리 가져오기

        print(f"Field: {field_name}, Value: {value}")  # 디버깅용 로그

        if field_name == 'username':
            if len(value) < 4:
                response_data.update({
                    'valid': False,
                    'message': '아이디는 4자 이상이어야 합니다.'
                })
            elif not re.match(r'^[a-zA-Z][\w.@+-]+\Z', value):
                response_data.update({
                    'valid': False,
                    'message': '영문자로 시작하고, 영문/숫자/일부 특수문자만 사용 가능합니다.'
                })
            elif get_user_model().objects.filter(username=value).exists():
                response_data.update({
                    'valid': False,
                    'message': '이미 사용 중인 아이디입니다.'
                })

        elif field_name == 'email':
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                response_data.update({
                    'valid': False,
                    'message': '유효한 이메일 주소를 입력해주세요.'
                })
            elif get_user_model().objects.filter(email=value).exists():
                response_data.update({
                    'valid': False,
                    'message': '이미 사용 중인 이메일입니다.'
                })

        elif field_name == 'nickname':
            if len(value) < 2:
                response_data.update({
                    'valid': False,
                    'message': '닉네임은 2자 이상이어야 합니다.'
                })
            elif not re.match(r'^[가-힣a-zA-Z0-9\s]+$', value):
                response_data.update({
                    'valid': False,
                    'message': '한글, 영문, 숫자만 사용 가능합니다.'
                })

        elif field_name == 'password1':
            if len(value) < 8:
                response_data.update({
                    'valid': False,
                    'message': '비밀번호는 8자 이상이어야 합니다.'
                })
            elif value.isdigit():
                response_data.update({
                    'valid': False,
                    'message': '숫자만으로는 비밀번호를 설정할 수 없습니다.'
                })

        print(f"Validation result: {response_data}")  # 디버깅용 로그
        return JsonResponse(response_data)

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")  # 디버깅용 로그
        return JsonResponse({
            'valid': False,
            'message': '잘못된 요청 형식입니다.'
        }, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n=== ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        print("=============\n")
        return JsonResponse({
            'valid': False,
            'message': f'검증 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

@require_POST
@csrf_exempt # 실제 프로덕션에서는 CSRF 토큰을 제대로 처리해야 합니다.
def verify_email_code(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            entered_code = data.get('code')
            email = data.get('email') # 인증 시도하는 이메일도 함께 받음

            session_code = request.session.get('verification_code')
            session_email = request.session.get('verification_email')

            if not entered_code:
                return JsonResponse({'valid': False, 'message': '인증번호를 입력해주세요.'}, status=400)

            if session_email != email:
                # 이메일이 변경된 경우, 이전 인증 코드는 무효화
                return JsonResponse({'valid': False, 'message': '이메일 정보가 변경되었습니다. 다시 인증번호를 전송해주세요.'}, status=400)

            if session_code == entered_code:
                # 인증 성공 시, 세션에 인증 완료 상태 저장 (선택 사항)
                request.session['email_verified_for_signup'] = True
                request.session['verified_email_for_signup'] = email # 어떤 이메일로 인증했는지 저장
                return JsonResponse({'valid': True, 'message': '인증번호가 확인되었습니다.'})
            else:
                return JsonResponse({'valid': False, 'message': '인증번호가 일치하지 않습니다.'})

        except json.JSONDecodeError:
            return JsonResponse({'valid': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
        except Exception as e:
            # 로깅 추가 권장
            print(f"Error in verify_email_code: {e}")
            return JsonResponse({'valid': False, 'message': '서버 오류가 발생했습니다.'}, status=500)
    return JsonResponse({'valid': False, 'message': '잘못된 접근입니다.'}, status=403)       
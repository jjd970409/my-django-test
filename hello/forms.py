from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '아이디를 입력하세요'})
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '비밀번호를 입력하세요'})
    )
    
    error_messages = {
        'invalid_login': _(
            "아이디 또는 비밀번호가 올바르지 않습니다. "
            "다시 시도해주세요."
        ),
        'inactive': _("이 계정은 비활성화되었습니다."),
    }

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='아이디',
        help_text='''<ul class="text-muted small">
            <li>150자 이하의 영문, 숫자, @/./+/-/_만 사용 가능합니다.</li>
            <li>다른 사람의 개인정보를 도용하지 마세요.</li>
        </ul>''',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디를 입력하세요'
        })
    )

    nickname = forms.CharField(
        label='닉네임',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '사용하실 닉네임을 입력하세요'
        }),
        help_text='다른 사람에게 보여질 이름입니다.'
    )

    password1 = forms.CharField(
        label='비밀번호',
        help_text='''
        <ul class="text-muted small">
            <li>다른 개인 정보와 유사한 비밀번호는 사용할 수 없습니다.</li>
            <li>비밀번호는 최소 8자 이상이어야 합니다.</li>
            <li>숫자만으로 된 비밀번호는 사용할 수 없습니다.</li>
            <li>자주 사용하는 비밀번호는 안전하지 않습니다.</li>
        </ul>
        ''',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요'
        })
    )
    
    password2 = forms.CharField(
        label='비밀번호 확인',
        help_text='<span class="text-muted small">확인을 위해 이전과 동일한 비밀번호를 입력하세요.</span>',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호를 한 번 더 입력하세요'
        })
    )

    email = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '예) example@example.com'
        })
    )
    
    email_verification_code = forms.CharField(
        label='이메일 인증번호',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일로 전송된 인증번호를 입력하세요'
        })
    )
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'nickname', 'email', 'password1', 'password2')
        labels = {
            'username': '아이디',
            'nickname': '닉네임',
            'email': '이메일',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field_name].label
            })

        # 에러 메시지 한국어로 변경
        self.fields['username'].error_messages = {
            'required': '아이디를 입력해주세요.',
            'unique': '이미 사용 중인 아이디입니다.',
            'invalid': '유효한 아이디를 입력하세요.',
        }
        self.fields['email'].error_messages = {
            'required': '이메일을 입력해주세요.',
            'invalid': '유효한 이메일 주소를 입력하세요.',
            'unique': '이미 사용 중인 이메일입니다.',
        }
        self.fields['password2'].error_messages = {
            'required': '비밀번호 확인을 입력해주세요.',
            'password_mismatch': '비밀번호가 일치하지 않습니다.',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용 중인 이메일입니다.')
        return email
    
    def generate_verification_code(self):
        """6자리 랜덤 인증번호 생성"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_verification_email(self, email, code):
        """이메일로 인증번호 전송"""
        subject = '[회원가입] 이메일 인증번호 안내'
        message = f'회원가입을 위한 인증번호는 [{code}] 입니다.'
        from_email = 'noreply@yourdomain.com'  # 실제 도메인으로 변경 필요
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # 아이디 길이 검사
        if len(username) < 4:
            raise ValidationError('아이디는 4자 이상이어야 합니다.')
            
        # 아이디 형식 검사 (영문자로 시작, 영문/숫자/특수문자(@/./+/-/_)만 허용)
        if not re.match(r'^[a-zA-Z][\w.@+-]+\Z', username):
            raise ValidationError('아이디는 영문자로 시작해야 하며, 영문/숫자/일부 특수문자(@/./+/-/_)만 사용 가능합니다.')
            
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        
        # 닉네임 길이 검사
        if len(nickname) < 2:
            raise ValidationError('닉네임은 2자 이상이어야 합니다.')
            
        # 닉네임에 특수문자 사용 제한
        if not re.match(r'^[가-힣a-zA-Z0-9\s]+$', nickname):
            raise ValidationError('닉네임에는 한글, 영문, 숫자만 사용 가능합니다.')
            
        return nickname

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # 비밀번호 길이 검사
        if len(password1) < 8:
            raise ValidationError('비밀번호는 8자 이상이어야 합니다.')
            
        # 숫자만 있는지 확인
        if password1.isdigit():
            raise ValidationError('비밀번호는 숫자로만 구성할 수 없습니다.')
            
        # 대문자, 소문자, 숫자 중 2가지 이상 조합 필수
        has_upper = any(c.isupper() for c in password1)
        has_lower = any(c.islower() for c in password1)
        has_digit = any(c.isdigit() for c in password1)
        
        if sum([has_upper, has_lower, has_digit]) < 2:
            raise ValidationError('비밀번호는 대문자, 소문자, 숫자 중 2가지 이상을 조합해야 합니다.')
            
        # 연속된 문자나 숫자 제한 (예: 1234, abcd)
        for i in range(len(password1) - 2):
            if (ord(password1[i+1]) == ord(password1[i]) + 1 and 
                ord(password1[i+2]) == ord(password1[i]) + 2):
                raise ValidationError('너무 간단한 연속된 문자나 숫자는 사용할 수 없습니다.')
                
        # 동일한 문자 반복 제한 (예: aaaa, 1111)
        for i in range(len(password1) - 3):
            if password1[i] == password1[i+1] == password1[i+2] == password1[i+3]:
                raise ValidationError('동일한 문자를 4번 이상 연속으로 사용할 수 없습니다.')
                
        return password1

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email_verification_code = cleaned_data.get('email_verification_code')
        session_code = self.data.get('session_verification_code')  # 세션에서 가져오기
        
        # 이메일 인증번호 검증
        if email_verification_code and session_code:
            if email_verification_code != session_code:
                self.add_error('email_verification_code', '인증번호가 일치하지 않습니다.')
        
        # 비밀번호와 아이디가 유사한지 확인
        username = cleaned_data.get('username')
        password1 = cleaned_data.get('password1')
        
        if username and password1:
            if username in password1 or password1 in username:
                self.add_error('password1', '비밀번호는 아이디와 유사하게 설정할 수 없습니다.')
        
        # 생년월일 유효성 검사 (필요한 경우)
        # birth_date = cleaned_data.get('birth_date')
        # if birth_date:
        #     today = date.today()
        #     age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        #     if age < 14:
        #         self.add_error('birth_date', '만 14세 이상만 가입 가능합니다.')
        
        return cleaned_data
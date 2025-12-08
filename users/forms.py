from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    interest = forms.CharField(max_length=100, help_text='관심 분야를 입력하세요.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',) # email 필드 제거

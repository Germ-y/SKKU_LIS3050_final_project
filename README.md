# NextGen Research Portal

이 프로젝트는 Django 프레임워크를 사용하여 최신 AI 연구 트렌드를 한곳에서 볼 수 있고, 관심 분야 기반으로 개인 맞춤 논문을 추천해주는 웹 애플리케이션입니다.

## 🚀 전체 구조 (폴더 + 기능 흐름)

```
project_root/
│
├── config/                # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── users/                 # 회원가입/로그인 앱
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── templates/users/
│       ├── signup.html
│       ├── login.html
│       └── home.html
│
├── papers/                # 크롤링 + 추천 기능
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── crawler.py         # BeautifulSoup 크롤러
│   ├── admin.py
│   └── templates/papers/
│       ├── list.html
│       └── detail.html
│
├── templates/
│   └── base.html          # hero-section + layout
│
├── manage.py              # Django 관리 스크립트
└── requirements.txt       # 프로젝트 의존성 목록
```

## 🧱 1. settings.py 기본 설정 (MySQL 포함)

`config/settings.py`에 포함된 데이터베이스 및 앱 설정입니다.

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nextgen_db',
        'USER': 'root',
        'PASSWORD': 'your_password',   # Cloud SQL 비밀번호
        'HOST': 'your.mysql.ip',       # Cloud SQL public IP
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

INSTALLED_APPS = [
    # ...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'papers',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        # ...
    }
]
```

## 👤 2. User & Profile 모델 (`users/models.py`)

Django의 기본 `User` 모델을 사용하고, 사용자의 관심 분야를 저장하기 위한 `Profile` 모델을 1:1로 연결합니다.

```python
# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interest = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

## 📝 3. 회원가입 폼 (`users/forms.py`)

Django의 `UserCreationForm`을 상속받아 관심 분야(`interest`) 필드를 추가한 회원가입 폼입니다.

```python
# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    interest = forms.CharField(max_length=100, help_text='관심 분야를 입력하세요.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
```

## 🔐 4. views.py (회원가입 기능 완성)

회원가입 시 `User`와 `Profile`을 함께 생성하고, 성공 시 바로 로그인 처리 후 논문 목록 페이지로 이동시키는 뷰 로직입니다.

```python
# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignupForm
from django.contrib.auth import login

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.interest = form.cleaned_data.get('interest')
            user.save()
            messages.success(request, "회원가입 완료!")
            login(request, user) # 회원가입 후 바로 로그인
            return redirect("paper_list")
    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})
```

## 🌐 5. users/urls.py

회원가입, 로그인, 로그아웃 URL 라우팅 설정입니다. Django의 내장 `LoginView`와 `LogoutView`를 사용합니다.

```python
# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
```

## 🧱 6. 논문 모델 (`papers/models.py`)

논문 정보를 저장하는 모델입니다.

```python
# papers/models.py
from django.db import models

class Paper(models.Model):
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=300)
    summary = models.TextField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title
```

## 🕷 7. 웹 크롤러 (`papers/crawler.py`)

arXiv에서 논문 데이터를 크롤링하는 기능을 담당합니다.

```python
# papers/crawler.py
import requests
from bs4 import BeautifulSoup
from .models import Paper

def crawl_arxiv():
    # 이전에 크롤링한 데이터를 모두 삭제
    Paper.objects.all().delete()
    
    url = "https://arxiv.org/list/cs.AI/recent"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    papers = soup.select("dl > dt")
    details = soup.select("dl > dd")

    for item, detail in zip(papers[:20], details[:20]): # 20개만 저장
        title = detail.find("div", class_="list-title").text.replace("Title:", "").strip()
        authors = detail.find("div", class_="list-authors").text.replace("Authors:", "").strip()
        summary = detail.find("p", class_="mathjax").text.strip()
        
        # 카테고리 추출 로직 추가
        subjects_div = detail.find("div", class_="list-subjects")
        category_text = subjects_div.text.replace("Subjects:", "").strip()
        primary_category = category_text.split(';')[0].split('(')[0].strip()

        Paper.objects.create(
            title=title,
            authors=authors,
            summary=summary,
            category=primary_category  # 추출된 주 카테고리를 저장
        )
```

## 📄 8. 논문 리스트 페이지 (`papers/views.py`)

로그인한 사용자의 관심 분야(`interest`)에 따라 논문을 추천하는 뷰 로직입니다. `@login_required` 데코레이터를 통해 로그인된 사용자만 접근할 수 있습니다.

```python
# papers/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Paper
from .crawler import crawl_arxiv

@login_required
def paper_list(request):
    # 데이터베이스에 논문이 하나도 없으면 크롤링 실행
    if not Paper.objects.exists():
        crawl_arxiv()

    interest = request.user.profile.interest
    
    if interest:
        # 관심 분야와 관련된 논문을 필터링합니다.
        papers = Paper.objects.filter(category__icontains=interest)
    else:
        # 관심 분야가 설정되지 않은 경우 모든 논문을 보여줍니다.
        papers = Paper.objects.all()

    return render(request, "papers/list.html", {"papers": papers, "interest": interest})

@login_required
def paper_detail(request, pk):
    paper = Paper.objects.get(id=pk)
    return render(request, "papers/detail.html", {"paper": paper})
```

## 🔗 9. papers/urls.py

논문 앱의 URL 라우팅 설정입니다.

```python
# papers/urls.py
from django.urls import path
from .views import paper_list, paper_detail

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("<int:pk>/", paper_detail, name="paper_detail"),
]
```

## 🧩 10. config/urls.py 최종 연결

프로젝트의 메인 URL 설정입니다.

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("users.urls")),
    path('papers/', include("papers.urls")),
]
```

## 🖥 11. base.html (hero-section 포함 기본 프레임)

모든 페이지의 기본 레이아웃을 제공하는 템플릿입니다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextGen Portal</title>
    <style>
        /* ... CSS styles ... */
    </style>
</head>
<body>

<header>
    <h1>NextGen Research Portal</h1>
</header>

<section class="hero">
    <h2>최신 AI 연구 트렌드를 한 곳에서</h2>
    <p>관심분야 기반 개인 맞춤 논문 추천</p>
</section>

<main>
    {% block content %}
    {% endblock %}
</main>

<footer>
    <p>© 2025 NextGen System</p>
</footer>

</body>
</html>
```

## 📄 12. 논문 리스트 템플릿 (`papers/templates/papers/list.html`)

논문 목록을 표시하는 템플릿입니다.

```html
{% extends "base.html" %}
{% block content %}
<h2>추천 논문 목록</h2>

{% for p in papers %}
    <div>
        <h3><a href="{% url 'paper_detail' p.id %}">{{ p.title }}</a></h3>
        <p><strong>Authors:</strong> {{ p.authors }}</p>
        <p><strong>Category:</strong> {{ p.category }}</p>
    </div>
    <hr>
{% empty %}
    <p>해당 관심 분야의 논문이 없습니다.</p>
{% endfor %}

{% endblock %}
```

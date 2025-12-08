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
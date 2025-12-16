from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Paper
from .crawler import crawl_arxiv
from users.models import Profile

@login_required
def paper_list(request):
    user_profile = Profile.objects.get(user=request.user)
    interest_code = user_profile.interest

    if interest_code and not Paper.objects.filter(category=interest_code).exists():
        crawl_arxiv(interest_code)

    if interest_code:
        papers = Paper.objects.filter(category=interest_code)
    else:
        papers = Paper.objects.all()

    interest_name = next((name for code, name in user_profile.INTEREST_CHOICES if code == interest_code), "모든 분야")

    return render(request, "papers/list.html", {"papers": papers, "interest": interest_name})

@login_required
def paper_detail(request, pk):
    paper = Paper.objects.get(id=pk)
    return render(request, "papers/detail.html", {"paper": paper})
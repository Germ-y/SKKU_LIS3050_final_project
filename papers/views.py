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
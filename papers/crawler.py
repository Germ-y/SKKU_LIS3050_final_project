import requests
from bs4 import BeautifulSoup
from .models import Paper

def crawl_arxiv():
    url = "https://arxiv.org/list/cs.AI/pastweek?show=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    entries = soup.find_all("dt")
    details = soup.find_all("dd")

    count = 0

    for dt, dd in zip(entries, details):

        # ----------- 1) 논문 ID → 상세 링크 생성 -----------
        paper_id = dt.find("a").text.strip()
        detail_url = f"https://arxiv.org/abs/{paper_id}"

        # ----------- 2) PDF 링크 -----------
        pdf_a = dd.find("a", title="Download PDF")
        pdf_url = f"https://arxiv.org{pdf_a['href']}" if pdf_a else None

        # ----------- 3) 제목(title) -----------
        title_div = dd.find("div", class_="list-title mathjax")
        if not title_div:
            continue
        title = title_div.text.replace("Title:", "").strip()

        # ----------- 4) 저자(authors) -----------
        authors_div = dd.find("div", class_="list-authors")
        authors = ", ".join(a.text.strip() for a in authors_div.find_all("a"))

        # ----------- 5) 카테고리(category) -----------
        subject_span = dd.find("span", class_="primary-subject")
        category = subject_span.text.strip() if subject_span else "Unknown"

        # ----------- 6) 중복 방지 -----------
        if Paper.objects.filter(title=title).exists():
            continue

        # ----------- 7) DB 저장 -----------
        Paper.objects.create(
            title=title,
            authors=authors,
            category=category,
            detail_url=detail_url,
            pdf_url=pdf_url,
        )

        count += 1

    print(f"[교안 수준 크롤링 완료] {count}개 저장됨")

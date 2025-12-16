import requests
from bs4 import BeautifulSoup
from .models import Paper

def crawl_arxiv(interest_code):
    url = f"https://arxiv.org/list/{interest_code}/pastweek?show=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    entries = soup.find_all("dt")
    details = soup.find_all("dd")

    count = 0

    for dt, dd in zip(entries, details):
        paper_id_tag = dt.find("a", title="Abstract")
        if not paper_id_tag:
            continue
        paper_id = paper_id_tag['href'].replace("/abs/", "")
        detail_url = f"https://arxiv.org/abs/{paper_id}"

        pdf_url = f"https://arxiv.org/pdf/{paper_id}"

        title_div = dd.find("div", class_="list-title mathjax")
        if not title_div:
            continue
        title = title_div.text.replace("Title:", "").strip()

        authors_div = dd.find("div", class_="list-authors")
        authors = ", ".join(a.text.strip() for a in authors_div.find_all("a"))

        if Paper.objects.filter(title=title).exists():
            continue

        Paper.objects.create(
            title=title,
            authors=authors,
            category=interest_code,
            detail_url=detail_url,
            pdf_url=pdf_url,
        )
        
        count += 1
        
        if count==5:
            break

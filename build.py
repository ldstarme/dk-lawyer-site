#!/usr/bin/env python3
"""columns/src/*.md -> columns/<slug>.html, columns/index.html, index.html 최근 칼럼, sitemap.xml
frontmatter: title, slug, date(최초 작성), updated(갱신), category, summary, original(네이버 원문 URL, 선택)
"""
import re, glob, os, json, html, datetime
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://dk-lawyer.co.kr"
SRC = os.path.join(ROOT, "columns", "src")

HEAD = """<!doctype html>
<html lang="ko">
<head>
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-MM5RDXLQ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | 이동규 변호사의 기록</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/">이동규 변호사의 기록<small>DK-LAWYER.CO.KR</small></a>
    <nav class="nav">
      <a href="/"{on_home}>소개</a>
      <a href="/columns/"{on_col}>칼럼</a>
      <a href="/cases.html"{on_cases}>해결 사례</a>
      <a href="/contact.html" class="cta{on_contact}">상담 안내</a>
    </nav>
  </div>
</header>
"""

FOOT = """<footer class="site-foot">
  <div class="wrap">
    이동규 변호사의 기록 · 위솔브 법률사무소 변호사 이동규<br>
    서울특별시 종로구 청계천로 71 계원빌딩 10층 · 전화 02-2138-3484 · 팩스 02-2138-3486<br>
    <a href="https://blog.naver.com/dk-lawyer" target="_blank" rel="noopener">네이버 블로그</a> · <a href="https://www.lawtalk.co.kr/directory/profile/5456-이동규" target="_blank" rel="noopener">로톡</a> · <a href="https://open.kakao.com/o/sgFQW5Pe" target="_blank" rel="noopener">카카오톡 상담</a> · 긴급 상담 010-9174-3289 · <a href="/contact.html">상담 안내</a><br>
    이 사이트의 글은 일반적인 법률 정보이며 개별 사건에 대한 법률 의견이 아닙니다.<br>
    이 사이트는 방문 통계 확인을 위해 구글 애널리틱스(쿠키)를 사용하며, 브라우저 설정에서 쿠키 저장을 거부할 수 있습니다.
  </div>
</footer>
</body>
</html>
"""

AUTHOR = """<div class="author">
  <b>글쓴이 변호사 이동규</b> · 위솔브 법률사무소 파트너 변호사 · 대한변호사협회 대의원<br>
  형사, 교통사고·보험, 부동산·임대차 사건을 직접 맡아 처리하며, 사건에서 정리한 법률 쟁점을 이곳에 기록합니다.
  {orig}
</div>
<div class="cta-box">
  <p><b>비슷한 상황이신가요?</b></p>
  <p>사건의 경위와 가지고 계신 자료를 말씀해 주시면, 가능한 것과 어려운 것을 처음부터 분명하게 말씀드립니다.</p>
  <a class="btn btn-call" href="tel:01091743289">긴급 상담 010-9174-3289</a>
  <a class="btn btn-kakao" href="https://open.kakao.com/o/sgFQW5Pe" target="_blank" rel="noopener">카카오톡 오픈채팅</a>
  <a class="btn btn-lawtalk" href="https://www.lawtalk.co.kr/directory/profile/5456-이동규" target="_blank" rel="noopener">로톡 예약 상담</a>
</div>
"""

def parse(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    meta = {}
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    meta["body"] = m.group(2).strip()
    meta.setdefault("slug", os.path.splitext(os.path.basename(path))[0])
    return meta

def kdate(s):
    y, mo, d = s.split("-")
    return f"{y}. {int(mo)}. {int(d)}."

def render_post(p):
    body_html = markdown.markdown(p["body"], extensions=["tables"])
    url = f"{SITE}/columns/{p['slug']}.html"
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["summary"],
        "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
        "author": {"@type": "Person", "name": "이동규", "jobTitle": "변호사", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "이동규 변호사의 기록"},
        "mainEntityOfPage": url, "inLanguage": "ko",
    }, ensure_ascii=False)
    meta_line = f"{p['category']} · 작성 {kdate(p['date'])}"
    if p.get("updated") and p["updated"] != p["date"]:
        meta_line += f" · 갱신 {kdate(p['updated'])}"
    orig = f'<br>원문은 <a href="{p["original"]}" target="_blank" rel="noopener">네이버 블로그</a>에 {kdate(p["date"])} 처음 올렸고, 이 글은 현행 법령·판례에 맞게 고쳐 쓴 것입니다.' if p.get("original") else ""
    out = HEAD.format(title=html.escape(p["title"]), desc=html.escape(p["summary"]), url=url, ld=ld,
                      on_home="", on_col=' class="on"', on_cases="", on_contact="")
    out += f"""<article class="article">
  <div class="meta">{meta_line}</div>
  <h1>{html.escape(p['title'])}</h1>
  <div class="summary">{html.escape(p['summary'])}</div>
  {body_html}
  {AUTHOR.format(orig=orig)}
</article>
"""
    out += FOOT
    open(os.path.join(ROOT, "columns", p["slug"] + ".html"), "w", encoding="utf-8").write(out)
    return url

def li(p):
    return f"""      <li>
        <time>{kdate(p.get('updated', p['date']))}</time>
        <div><span class="cat">{html.escape(p['category'])}</span><a class="t" href="/columns/{p['slug']}.html">{html.escape(p['title'])}</a>
        <div class="s">{html.escape(p['summary'])}</div></div>
      </li>
"""

def render_page(mdfile, slug, title, desc, nav):
    p = parse(mdfile)
    body_html = markdown.markdown(p["body"], extensions=["tables"])
    url = f"{SITE}/{slug}.html"
    on = {"on_home":"", "on_col":"", "on_cases":"", "on_contact":""}
    on[nav] = ' class="on"'
    out = HEAD.format(title=html.escape(title), desc=html.escape(desc), url=url, ld="{}", **on)
    out += f'<section>\n  <div class="wrap page-body">\n{body_html}\n  </div>\n</section>\n' + FOOT
    open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8").write(out)

def main():
    render_page(os.path.join(ROOT, "pages", "cases.md"), "cases", "해결 사례", "이동규 변호사가 직접 맡아 처리한 형사·민사·부동산·교통사고 사건의 해결 사례.", "on_cases")
    posts = [parse(f) for f in glob.glob(os.path.join(SRC, "*.md"))]
    posts.sort(key=lambda p: (p.get("updated", p["date"]), p["date"]), reverse=True)
    urls = [render_post(p) for p in posts]

    # columns index
    cats = {}
    for p in posts:
        cats.setdefault(p["category"], []).append(p)
    idx = HEAD.format(title="칼럼", desc="이동규 변호사가 직접 쓴 형사, 교통사고·보험, 부동산 법률 칼럼.",
                      url=SITE + "/columns/", ld="{}", on_home="", on_col=' class="on"', on_cases="", on_contact="")
    idx += '<section>\n  <div class="wrap">\n    <h2>칼럼 <small>형사 · 교통사고·보험 · 부동산 · 기업자문</small></h2>\n    <ul class="post-list">\n'
    idx += "".join(li(p) for p in posts)
    idx += "    </ul>\n  </div>\n</section>\n" + FOOT
    open(os.path.join(ROOT, "columns", "index.html"), "w", encoding="utf-8").write(idx)

    # home recent 3
    home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    new_list = '    <ul class="post-list">\n' + "".join(li(p) for p in posts[:3]) + "    </ul>\n"
    home = re.sub(r'    <ul class="post-list">\n.*?    </ul>\n', new_list, home, count=1, flags=re.S)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(home)

    # sitemap
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in [(SITE + "/", today), (SITE + "/columns/", today), (SITE + "/contact.html", today), (SITE + "/cases.html", today)] + \
                 [(u, p.get("updated", p["date"])) for u, p in zip(urls, posts)]:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"{len(posts)} posts built")

if __name__ == "__main__":
    main()

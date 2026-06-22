import io
import requests
import re
import concurrent.futures
from typing import List
from src.models import Paper

# PyPDF2 仅在"精读"抓 PDF 全文时才需要。缺它不应让整个 pipeline 无法导入，
# 因此延迟为可选依赖：未安装时 PDF 全文解析自动降级为空，不影响其余功能。
try:
    import PyPDF2
except ImportError:  # pragma: no cover
    PyPDF2 = None

def fetch_code_url(arxiv_id: str) -> tuple[str, int]:
    # Strip version suffix (e.g., 'v1', 'v2') from arxiv_id for HF/PWC APIs
    base_arxiv_id = re.sub(r'v\d+$', '', arxiv_id)
    # Strategy 1: Try HuggingFace Papers HTML scraping (PWC API often redirects now)
    hf_url = f"https://huggingface.co/papers/{base_arxiv_id}"
    try:
        resp = requests.get(hf_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if resp.status_code == 200:
            match = re.search(r'(?:&quot;|")githubRepo(?:&quot;|")\s*:\s*(?:&quot;|")https://github\.com/([^/]+)/([^&"\'\\]+)', resp.text)
            if not match:
                match = re.search(r'github\.com/([^/]+)/([^/"\'<&\\]+)', resp.text)
            if match:
                owner = match.group(1)
                repo = match.group(2).rstrip('.')
                url = f"https://github.com/{owner}/{repo}"
                if "huggingface" not in owner.lower():  # Filter out HF generic links
                    stars = 0
                    try:
                        api_resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}", timeout=3)
                        if api_resp.status_code == 200:
                            stars = api_resp.json().get("stargazers_count", 0)
                        elif api_resp.status_code in (403, 429):
                            html_resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                            smatch = re.search(r'id="repo-stars-counter-star"[^>]*title="([\d,]+)"', html_resp.text)
                            if smatch:
                                stars = int(smatch.group(1).replace(",", ""))
                    except:
                        pass
                    return url, stars
    except Exception:
        pass

    # Strategy 2: Fallback to old PapersWithCode API
    pwc_url = f"https://paperswithcode.com/api/v1/papers/?arxiv_id={base_arxiv_id}"
    try:
        resp = requests.get(pwc_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("count", 0) > 0:
                results = data.get("results", [])
                if results and "repository_url" in results[0]:
                    url = results[0]["repository_url"] or ""
                    stars = results[0].get("stars", 0)
                    return url, stars
    except Exception:
        pass
    return "", 0

def fetch_image_url(arxiv_id: str) -> str:
    url = f"https://browse.arxiv.org/html/{arxiv_id}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            # find first <img> tag src
            match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
            if match:
                src = match.group(1)
                if not src.startswith("http"):
                    if src.startswith("/"):
                        src = "https://browse.arxiv.org" + src
                    else:
                        src = f"https://browse.arxiv.org/html/{arxiv_id}/{src}"
                return src
    except Exception:
        pass
    return ""

def fetch_full_text(arxiv_id: str) -> str:
    url = f"https://browse.arxiv.org/html/{arxiv_id}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            html = resp.text
            # Use regex to strip HTML tags
            text = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.IGNORECASE|re.DOTALL)
            text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
            text = re.sub(r'<math[^>]*>.*?</math>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                return text[:40000] # truncate to ~40k chars to save tokens and time
    except Exception:
        pass
    return fetch_pdf_text(arxiv_id)

def fetch_pdf_text(arxiv_id: str) -> str:
    if PyPDF2 is None:  # 未安装 PyPDF2：跳过 PDF 解析，让精读优雅降级而非报错
        return ""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=60)
        if resp.status_code == 200:
            pdf_file = io.BytesIO(resp.content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for i in range(len(reader.pages)):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            return text[:40000]
    except Exception:
        pass
    return ""

def enrich_paper(paper: Paper, fetch_full: bool = False):
    if paper.source == "arxiv":
        arxiv_id = paper.paper_id.replace("arxiv:", "")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_code = executor.submit(fetch_code_url, arxiv_id)
            future_img = executor.submit(fetch_image_url, arxiv_id)
            future_text = executor.submit(fetch_full_text, arxiv_id) if fetch_full else None
            
            code_url, stars = future_code.result()
            paper.code_url = code_url
            paper.github_stars = stars
            paper.image_url = future_img.result()
            if future_text:
                paper.full_text = future_text.result()

def enrich_papers(papers: List[Paper], fetch_full: bool = False) -> List[Paper]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(lambda p: enrich_paper(p, fetch_full), papers)
    return papers

def enrich_full_text_only(papers: List[Paper]):
    def fetch_text(p):
        if p.source == "arxiv" and not p.full_text:
            arxiv_id = p.paper_id.replace("arxiv:", "")
            p.full_text = fetch_full_text(arxiv_id)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(fetch_text, papers)

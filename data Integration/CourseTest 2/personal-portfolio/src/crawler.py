import argparse
import os
import requests
from bs4 import BeautifulSoup

def fetch_html(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def attrs_text(tag):
    if not tag.attrs:
        return ""
    parts = []
    # 优先显示 id/class，然后其它若干属性
    if tag.has_attr("id"):
        parts.append(f'id="{tag["id"]}"')
    if tag.has_attr("class"):
        parts.append(f'class="{" ".join(tag["class"])}"')
    # 其余属性（最多显示3个）
    others = [(k, v) for k, v in tag.attrs.items() if k not in ("id", "class")]
    for k, v in others[:3]:
        if isinstance(v, list):
            v = " ".join(v)
        parts.append(f'{k}="{v}"')
    return " " + " ".join(parts) if parts else ""

def traverse(soup, max_depth=6):
    root = soup.html if soup.html else soup
    lines = []
    def walk(node, depth, indent=""):
        if depth > max_depth:
            return
        for child in node.children:
            if getattr(child, "name", None):
                line = f"{indent}<{child.name}{attrs_text(child)}>"
                lines.append(line)
                walk(child, depth+1, indent + "  ")
    walk(root, 1, "")
    return lines

def save(outdir, name, lines):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path

def take_screenshot(url, outpath):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("Playwright 未安装或不可用，跳过截图。若需截图请执行: pip install playwright && python -m playwright install")
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.screenshot(path=outpath, full_page=True)
            browser.close()
        return outpath
    except Exception as e:
        print(f"截图失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="抓取页面并导出 HTML 文档结构")
    parser.add_argument("--url", "-u", default="http://localhost:8080", help="目标 URL（默认 http://localhost:8080）")
    parser.add_argument("--depth", "-d", type=int, default=6, help="结构输出深度（默认 6）")
    parser.add_argument("--out", "-o", default="results", help="输出目录（默认 results）")
    parser.add_argument("--screenshot", "-s", action="store_true", help="是否截取渲染后的页面截图（需 playwright）")
    args = parser.parse_args()

    html = fetch_html(args.url)
    if not html:
        print("无法获取页面 HTML，结束。")
        return

    soup = BeautifulSoup(html, "lxml")
    header = [
        f"# Source: {args.url}",
        ""
    ]
    structure = traverse(soup, max_depth=args.depth)
    if not structure:
        structure = ["(空结构)"]
    lines = header + structure
    outpath = save(args.out, "structure.txt", lines)
    print(f"已保存 HTML 结构到: {outpath}")

    if args.screenshot:
        png_path = os.path.join(args.out, "screenshot.png")
        ss = take_screenshot(args.url, png_path)
        if ss:
            print(f"已保存截图到: {ss}")

if __name__ == "__main__":
    main()
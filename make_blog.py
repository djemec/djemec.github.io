'''Generate a static HTML page for a blog post from a markdown file.

Usage:
    python make_blog.py path/to/post.md

Copies the .md into blogs/, updates blogs/blogs.json, and writes blog/<slug>.html.
'''

import sys, json, re, shutil, html
from pathlib import Path
from datetime import date
import markdown

ROOT = Path(__file__).resolve().parent
BLOGS_DIR = ROOT / 'blogs'
OUT_DIR = ROOT / 'blog'
MANIFEST = BLOGS_DIR / 'blogs.json'
SITE_URL = 'https://domenjemec.com'
GA_ID = 'G-CRV0D7Q5HX'

TEMPLATE = '''<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <meta name='description' content='{description}' />
  <title>{title} | Domen Jemec</title>
  <meta property='og:title' content='{title} | Domen Jemec' />
  <meta property='og:description' content='{description}' />
  <meta property='og:url' content='{url}' />
  <meta property='og:type' content='article' />
  <meta property='og:image' content='{SITE_URL}/resources/photo.jpg' />
  <meta property='article:author' content='Domen Jemec' />
  <meta property='article:published_time' content='{iso_date}' />
  <meta name='twitter:card' content='summary_large_image' />
  <meta name='twitter:site' content='@domenjemec' />
  <meta name='twitter:creator' content='@domenjemec' />
  <meta name='twitter:title' content='{title} | Domen Jemec' />
  <meta name='twitter:description' content='{description}' />
  <meta name='twitter:image' content='{SITE_URL}/resources/photo.jpg' />
  <link rel='canonical' href='{url}' />
  <meta name='author' content='Domen Jemec' />
  <meta name='robots' content='index, follow' />
  <style>
    :root{{
      --bg:#020810;
      --text:#ffffff;
      --muted:#8899aa;
      --accent:#00f5ff;
      --maxw:1400px;
      --mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;
      --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    html{{scroll-behavior:smooth}}
    body{{font-family:var(--sans);color:var(--text);line-height:1.6;background:var(--bg);font-size:18px}}
    a{{color:inherit;text-decoration:none}}
    .container{{max-width:var(--maxw);margin:0 auto;padding:0 2vw}}
    nav{{padding:15px 0 10px;display:flex;justify-content:space-between;align-items:center}}
    .logo{{font-size:30px;font-weight:700;color:var(--accent)}}
    .nav-social{{display:flex;gap:20px;align-items:center}}
    .nav-social a{{color:var(--muted);transition:all .1s;display:flex;align-items:center;justify-content:center}}
    .nav-social a:hover{{color:var(--accent)}}
    .nav-social svg{{width:22px;height:22px}}
    .nav-link{{font-size:14px;text-transform:uppercase;letter-spacing:2px;font-weight:600}}
    main{{padding:40px 0 80px;max-width:1000px;margin:0 auto}}
    .back-link{{display:inline-flex;align-items:center;gap:8px;color:var(--muted);font-size:14px;margin-bottom:32px;transition:color .15s}}
    .back-link:hover{{color:var(--accent)}}
    .back-link svg{{width:14px;height:14px}}
    article .post-date{{font-size:13px;color:var(--accent);font-family:var(--mono);margin-bottom:12px;text-transform:uppercase;letter-spacing:2px}}
    article h1{{font-size:clamp(28px,4vw,42px);font-weight:700;line-height:1.2;letter-spacing:-0.5px;margin-bottom:32px;background:linear-gradient(135deg,var(--text) 0%,var(--accent) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
    article h2{{font-size:22px;font-weight:600;color:var(--text);margin-top:40px;margin-bottom:16px}}
    article h3{{font-size:18px;font-weight:600;color:var(--text);margin-top:32px;margin-bottom:12px}}
    article p{{color:var(--muted);font-size:17px;line-height:1.85;margin-bottom:20px}}
    article a{{color:var(--accent);text-decoration:underline;text-underline-offset:3px}}
    article a:hover{{text-decoration:none}}
    article ul,article ol{{color:var(--muted);font-size:17px;line-height:1.85;margin-bottom:20px;padding-left:24px}}
    article li{{margin-bottom:8px}}
    article blockquote{{border-left:2px solid var(--accent);padding-left:20px;margin:24px 0;color:var(--muted);font-style:italic}}
    article code{{font-family:var(--mono);font-size:15px;background:rgba(0,245,255,.08);color:var(--accent);padding:2px 6px}}
    article pre{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);padding:18px 20px;margin:24px 0;overflow-x:auto;font-family:var(--mono);font-size:14px;line-height:1.6}}
    article pre code{{background:none;color:var(--text);padding:0;font-size:14px}}
    article img{{max-width:100%;height:auto;margin:24px 0}}
    article hr{{border:none;border-top:1px solid rgba(255,255,255,.07);margin:40px 0}}
    footer{{padding:36px 0;border-top:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:14px}}
    footer a{{color:var(--accent)}}
    @media(max-width:500px){{footer{{flex-direction:column;gap:10px;text-align:center}}}}
  </style>
  <!-- Google tag (gtag.js) -->
  <script async src='https://www.googletagmanager.com/gtag/js?id={GA_ID}'></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>
</head>
<body>
  <div class='container'>
    <nav>
      <a href='../index.html' class='logo'>Domen Jemec</a>
      <div class='nav-social'>
        <a href='../blog.html' class='nav-link'>Blog</a>
        <a href='https://www.linkedin.com/in/domenjemec/' target='_blank' rel='noreferrer' aria-label='LinkedIn'>
          <svg viewBox='0 0 24 24' fill='currentColor'><path d='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'/></svg>
        </a>
        <a href='https://github.com/djemec' target='_blank' rel='noreferrer' aria-label='GitHub'>
          <svg viewBox='0 0 24 24' fill='currentColor'><path d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/></svg>
        </a>
        <a href='https://x.com/domenjemec' target='_blank' rel='noreferrer' aria-label='Twitter'>
          <svg viewBox='0 0 24 24' fill='currentColor'><path d='M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z'/></svg>
        </a>
      </div>
    </nav>
    <hr>
    <main>
      <a class='back-link' href='../blog.html'>
        <svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M19 12H5M12 19l-7-7 7-7'/></svg>
        All posts
      </a>
      <article>
        <div class='post-date'>{display_date}</div>
        <h1>{title_html}</h1>
        {body_html}
      </article>
    </main>
    <footer>
      <div>&copy; {year} <a href='../index.html'>Domen Jemec</a></div>
      <div><a href='#'>I'm lazy, take me back to the top</a></div>
    </footer>
  </div>
</body>
</html>
'''


def extract_title(md_text):
    for line in md_text.splitlines():
        m = re.match(r'^#\s+(.+?)\s*$', line)
        if m:
            return m.group(1).strip()
    return None


def strip_title(md_text):
    lines = md_text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            del lines[i]
            while i < len(lines) and lines[i].strip() == '':
                del lines[i]
            break
    return '\n'.join(lines)


def extract_description(md_body, limit=155):
    for line in md_body.splitlines():
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('>') or s.startswith('-') or s.startswith('*'):
            continue
        s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
        s = re.sub(r'[*_`]', '', s)
        s = s.strip()
        if not s:
            continue
        if len(s) <= limit:
            return s
        cut = s[:limit].rsplit(' ', 1)[0]
        return cut + '…'
    return 'Writing by Domen Jemec.'


def format_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime('%B %-d, %Y').upper()


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return []


def save_manifest(entries):
    entries_sorted = sorted(entries, key=lambda e: e['date'], reverse=True)
    MANIFEST.write_text(json.dumps(entries_sorted, indent=2) + '\n')


def upsert_manifest(manifest, file_name, iso_date):
    for entry in manifest:
        if entry['file'] == file_name:
            return manifest
    manifest.append({'file': file_name, 'date': iso_date})
    return manifest


def main():
    if len(sys.argv) != 2:
        print(f'Usage: python {Path(__file__).name} path/to/post.md')
        sys.exit(1)

    src = Path(sys.argv[1]).expanduser().resolve()
    if not src.exists() or src.suffix.lower() != '.md':
        print(f'Error: {src} is not a markdown file')
        sys.exit(1)

    slug = src.stem
    md_dest = BLOGS_DIR / f'{slug}.md'
    html_dest = OUT_DIR / f'{slug}.html'
    OUT_DIR.mkdir(exist_ok=True)
    BLOGS_DIR.mkdir(exist_ok=True)

    if src.resolve() != md_dest.resolve():
        shutil.copyfile(src, md_dest)
        print(f'copied {src.name} -> blogs/{md_dest.name}')

    md_text = md_dest.read_text()
    title = extract_title(md_text) or slug.replace('_', ' ').title()
    body_md = strip_title(md_text)
    description = extract_description(body_md)

    manifest = load_manifest()
    existing = next((e for e in manifest if e['file'] == md_dest.name), None)
    iso_date = existing['date'] if existing else date.today().isoformat()
    manifest = upsert_manifest(manifest, md_dest.name, iso_date)
    save_manifest(manifest)

    body_html = markdown.markdown(body_md, extensions=['extra', 'sane_lists', 'nl2br'])

    url = f'{SITE_URL}/blog/{slug}.html'
    page = TEMPLATE.format(
        title=html.escape(title),
        title_html=html.escape(title),
        description=html.escape(description),
        url=url,
        iso_date=iso_date,
        display_date=format_date(iso_date),
        year=date.today().year,
        body_html=body_html,
        SITE_URL=SITE_URL,
        GA_ID=GA_ID,
    )
    html_dest.write_text(page)
    print(f'wrote blog/{html_dest.name}')
    print(f'manifest: {md_dest.name} @ {iso_date}')


if __name__ == '__main__':
    main()

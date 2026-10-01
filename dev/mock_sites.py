"""Mock live (8001) and staging (8002) sites with deliberate SEO differences."""
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def page(title, desc, canon, heads, imgs, schema="", robots="", words=200):
    h = "".join(f"<h{l}>{t}</h{l}>" for l, t in heads)
    im = "".join(f'<img src="{s}"' + (f' alt="{a}"' if a is not None else "") + ">" for s, a in imgs)
    return f"""<!doctype html><html><head><title>{title}</title>
<meta name="description" content="{desc}">
{f'<meta name="robots" content="{robots}">' if robots else ''}
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{title}">
{schema}</head><body><svg><title>icon</title></svg>{h}{im}<p>{'word ' * words}</p></body></html>"""

FAQ = '<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"T","url":"https://transcure.net/","logo":"x"},{"@type":"FAQPage","mainEntity":[]}]}</script>'
ORG = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"T","url":"https://stage.transcure.net/"}</script>'
BROKEN = '<script type="application/ld+json">{"@type": "WebPage", </script>'

L = "http://127.0.0.1:8001"
S = "http://127.0.0.1:8002"

LIVE = {
    "/": page("Home | TransCure", "Medical billing &amp; coding", L + "/", [(1, "Home"), (2, "Services")],
              [("/wp-content/uploads/2023/05/hero-1024x768.jpg", "Hero image")], FAQ),
    "/services/": page("Medical Billing Services", "We do billing", L + "/services/",
                       [(1, "Services"), (2, "Billing"), (2, "Coding"), (3, "ICD-10")],
                       [("/wp-content/uploads/2023/05/billing.jpg", "Billing team"),
                        ("/wp-content/uploads/2023/05/coding.png", "Coding"),
                        ("/wp-content/uploads/2023/05/gone.png", "Gone")], FAQ, words=500),
    "/about": page("About", "About us", L + "/about", [(1, "About")], []),
    "/contact/": page("Contact", "Contact us", L + "/contact/", [(1, "Contact")], []),
    "/blog/post/": page("Post", "Post desc", L + "/blog/post/", [(1, "Post")], [("/img/IMG_1234.jpg", "x")]),
}
STAGE = {
    "/": page("Home | TransCure", "Medical billing & coding", S + "/", [(1, "Home"), (2, "Services")],
              [("/wp-content/uploads/2023/05/hero.jpg", "Hero image")], FAQ),
    "/services/": page("Billing Services | TransCure", "We do billing", S + "/services/",
                       [(1, "Services"), (1, "Extra H1"), (2, "Billing"), (4, "ICD-10")],
                       [("/wp-content/uploads/2023/05/billing.webp", "Billing staff"),
                        ("https://cdn.example.com/media/coding.png", None),
                        ("/img/IMG_9999.jpg", "")], ORG + BROKEN, robots="noindex, nofollow", words=100),
    "/about/": page("About", "About us", S + "/about/", [(1, "About")], []),
    "/blog/post/": page("Post", "Post desc", L + "/blog/post/", [(1, "Post")], [("/img/IMG_1234.jpg", "x")]),
}
REDIRECTS_LIVE = {"/services": "/services/", "/contact": "/contact/", "/blog/post": "/blog/post/", "/about/": "/about"}
REDIRECTS_STAGE = {"/services": "/services/", "/about": "/about/"}
DUP_STAGE = {"/blog/post": "/blog/post/"}  # both variants 200

SITEMAP_INDEX = f'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{L}/page-sitemap.xml</loc></sitemap></sitemapindex>'
SITEMAP = '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
    f"<url><loc>{L}{p}</loc></url>" for p in LIVE) + "</urlset>"


def handler(pages, redirects, dup, is_live, auth=None):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body=b"", ctype="text/html; charset=utf-8", headers=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            p = self.path
            if auth and self.headers.get("Authorization") != auth:
                return self.send(401, b"auth")
            if is_live and p == "/robots.txt":
                return self.send(200, f"Sitemap: {L}/sitemap_index.xml\n".encode(), "text/plain")
            if is_live and p == "/sitemap_index.xml":
                return self.send(200, SITEMAP_INDEX.encode(), "application/xml")
            if is_live and p == "/page-sitemap.xml":
                return self.send(200, SITEMAP.encode(), "application/xml")
            if p in redirects:
                return self.send(301, headers={"Location": redirects[p]})
            if p in dup:
                return self.send(200, pages[dup[p]].encode())
            if p in pages:
                return self.send(200, pages[p].encode())
            self.send(404, b"not found")
    return H


def start(auth=None):
    import base64
    a = "Basic " + base64.b64encode(auth.encode()).decode() if auth else None
    for port, args in ((8001, (LIVE, REDIRECTS_LIVE, {}, True)), (8002, (STAGE, REDIRECTS_STAGE, DUP_STAGE, False, a))):
        srv = ThreadingHTTPServer(("127.0.0.1", port), handler(*args))
        threading.Thread(target=srv.serve_forever, daemon=True).start()

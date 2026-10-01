# SEO Migration Audit (Google Colab)

Compares every page of the live site (`https://transcure.net`) with its staging copy
(`https://stage.transcure.net`) and produces an Excel report of every SEO difference.

**Checks:** HTTP status · URL · trailing slash (+ redirect of the other variant) · meta title ·
meta description · canonical · robots/noindex · heading structure (H1–H6) · image alts ·
image file names · image URL structure · schema (JSON-LD + microdata) · Open Graph · hreflang ·
content length.

## Open it in Colab

**Option A — upload the file:** download [`seo_migration_audit.ipynb`](seo_migration_audit.ipynb),
go to <https://colab.research.google.com> → **File → Upload notebook** → pick the file.

**Option B — straight from GitHub:** in Colab, **File → Open notebook → GitHub** tab, tick
**Include private repos**, authorize, then choose `seotranscure-ui/migration-audit` and
`seo_migration_audit.ipynb`.

## Run it

1. **Cell ① Settings** — live/staging URLs are pre-filled. Add the staging username/password
   (HTTP basic auth) or a cookie if staging is protected. Set `MAX_URLS = 20` for a quick first test.
2. **Cell ② URL list** — choose one:
   - *Sitemap of live site* (auto-detected from `robots.txt` / `sitemap_index.xml`)
   - *Paste URLs* — one per line; add `, new-staging-url` for pages whose URL changed
   - *Upload CSV* — columns `live_url`, `stage_url` (optional)
3. **Runtime → Run all.** Cell ④ shows a summary; cell ⑤ downloads the report — choose
   *Summary + detail sheets*, *Summary only* (Excel), or *Summary only* (CSV).

Nothing to install: Colab already has every library the notebook uses.

## The report

| Sheet | Contents |
|---|---|
| Summary | Same table as shown in the notebook: every page, worst first, `#` = page number, coloured PASS/WARN/FAIL |
| Overview | FAIL / WARN / PASS counts per check |
| All issues | Every FAIL/WARN with live value, staging value and what's wrong |
| *one sheet per check* | Same, filtered to that check (e.g. only *Meta title* issues) |
| Images | Every image pair: live vs staging src, alt, name/alt/path match |
| All details | Everything, including passes |

**FAIL** = differs from live / broken. **WARN** = needs a human look (e.g. `noindex` on staging,
which is expected now but must be gone at launch).

## Notes

- Colab runs on Google's servers. If staging only allows office/VPN IPs, ask the developers to
  allow access or set up a username/password; otherwise every staging page shows 401/403.
- Pages are read as raw HTML. If the new site renders titles/headings with JavaScript only, tell
  us — a browser-rendering mode can be added.
- Re-run after each round of fixes, and once more against production right after launch
  (set `STAGE_BASE` to the production URL).

## Development

`dev/build_notebook.py` generates the notebook; `dev/run_test.py` runs it against local mock
sites with planted issues (`dev/mock_sites.py`):

```
pip install beautifulsoup4 lxml requests pandas openpyxl tqdm nbformat
python dev/build_notebook.py seo_migration_audit.ipynb
python dev/run_test.py seo_migration_audit.ipynb
```

"""Executes the notebook's code cells against the mock sites (no Colab needed)."""
import os, sys, json
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"
sys.path.insert(0, os.path.dirname(__file__))
import mock_sites
import pandas as pd

mock_sites.start(auth="seo:secret")
nb = json.load(open(sys.argv[1]))
cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
g = {"display": lambda x: print(x.data if hasattr(x, "data") else x)}
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 40)

exec(cells[0], g)  # settings
g.update(LIVE_BASE="http://127.0.0.1:8001", STAGE_BASE="http://127.0.0.1:8002",
         STAGE_USERNAME="seo", STAGE_PASSWORD="secret", DELAY_SECONDS=0, TIMEOUT=5)
exec(cells[1], g)  # URL list
g["URL_SOURCE"] = sys.argv[2] if len(sys.argv) > 2 else "Sitemap of live site"
g["PASTED_URLS"] = "/services/\nhttp://127.0.0.1:8001/about, /about-us/\n"
for c in cells[2:]:
    exec(c, g)

d = g["details_df"]
print(g["summary_df"][["live_url", "stage_status", "FAIL", "WARN"] + g["CHECKS"]].to_string())
print()
for _, r in d[d.status != "PASS"].iterrows():
    print(f"[{r.status}] {r.live_url.replace('http://127.0.0.1:8001','')} | {r.check}: {r.note}".replace("\n", " ⏎ "))

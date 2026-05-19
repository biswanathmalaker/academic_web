import re
import time
import requests
from django.utils import timezone

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from .models import Paper


# ---------------------------------------------------------------------------
# Load ADS token from secret_info.py at project root
# ---------------------------------------------------------------------------
def _get_ads_token():
    try:
        import importlib.util, os
        from django.conf import settings
        spec = importlib.util.spec_from_file_location(
            "secret_info",
            os.path.join(settings.BASE_DIR, "secret_info.py")
        )
        secret = importlib.util.module_from_spec(spec)   # ← was load_from_spec
        spec.loader.exec_module(secret)
        return secret.ADS_TOKEN.strip().strip('"').strip("'")
    except Exception as e:
        raise RuntimeError(f"Could not load ADS_TOKEN from secret_info.py: {e}")

# ---------------------------------------------------------------------------
# BibTeX parsing helpers
# ---------------------------------------------------------------------------

def _bibcode_from_adsurl(adsurl: str) -> str | None:
    """Extract bibcode from ADS URL, e.g.
    https://ui.adsabs.harvard.edu/abs/2023ApJ...951L..15K  →  2023ApJ...951L..15K
    """
    if not adsurl:
        return None
    match = re.search(r'/abs/([^/?\s]+)', adsurl)
    return match.group(1) if match else None


def extract_metadata(entry: str) -> dict:
    """Parse a BibTeX entry string into structured metadata dict."""
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode

    bib_database = bibtexparser.loads(entry, parser=parser)
    if not bib_database.entries:
        return {}

    e = bib_database.entries[0]

    arxiv_id = e.get("eprint", None)
    adsurl   = e.get("adsurl", None)

    data = {
        "key":     e.get("ID", "Unknown Key"),
        "title":   e.get("title", "Unknown Title"),
        "authors": e.get("author", "Unknown Author"),
        "year":    e.get("year", None),
        "journal": e.get("journal", "Unknown Journal"),
        "volume":  e.get("volume", None),
        "pages":   e.get("pages", None),
        "eid":     e.get("eid", None),
        "doi":     e.get("doi", None),
        "adsurl":  adsurl,
        "arxiv":   f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
        "bibcode": _bibcode_from_adsurl(adsurl),
    }

    # Clean journal string (encoding artifacts)
    if data["journal"]:
        data["journal"] = (
            data["journal"]
            .encode("utf-8", "ignore")
            .decode("utf-8")
            .replace("\x07", "A")
        )

    return data


def generate_identifier(first_author: str, year: int, exclude_pk=None) -> str:
    """Generate a unique key like weitz-2025, weitz-2025a, weitz-2025b …"""
    if not first_author or not year:
        return "unknown"

    base     = re.sub(r'[^a-z]', '', first_author.split(",")[0].lower())
    base_key = f"{base}-{year}"

    qs = Paper.objects.filter(key__startswith=base_key)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    existing = set(qs.values_list("key", flat=True))

    if base_key not in existing:
        return base_key

    suffix = ord("a")
    while True:
        candidate = f"{base_key}{chr(suffix)}"
        if candidate not in existing:
            return candidate
        suffix += 1


def save_bibtex(bibtex_entry: str, core: bool = True) -> Paper:
    """Create or update a Paper from a raw BibTeX string.
    Skips if same author+volume+pages already exists.
    """
    data = extract_metadata(bibtex_entry)
    data["bibtex"] = bibtex_entry
    data["core"]   = core

    if data["year"]:
        try:
            data["year"] = int(data["year"])
        except ValueError:
            data["year"] = None

    # Deduplicate by author + volume + pages
    existing = Paper.objects.filter(
        authors=data.get("authors"),
        volume=data.get("volume"),
        pages=data.get("pages"),
    ).first()
    if existing:
        return existing

    identifier = generate_identifier(
        first_author=data.get("authors", "unknown"),
        year=data.get("year"),
    )
    data["key"] = identifier

    paper, _ = Paper.objects.update_or_create(
        key=data["key"],
        defaults=data,
    )
    return paper


# ---------------------------------------------------------------------------
# ADS API helpers
# ---------------------------------------------------------------------------

ADS_SEARCH_URL = "https://api.adsabs.harvard.edu/v1/search/query"
ADS_BIBTEX_URL = "https://api.adsabs.harvard.edu/v1/export/bibtex"
ADS_BATCH_SIZE = 100   # max bibcodes per ADS request


def _ads_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _fetch_ads_metadata(bibcodes: list[str], token: str) -> list[dict]:
    """Fetch metadata for a list of bibcodes from ADS search endpoint.
    Handles batching automatically (100 per request).
    Returns a list of ADS doc dicts.
    """
    results = []
    for i in range(0, len(bibcodes), ADS_BATCH_SIZE):
        batch = bibcodes[i:i + ADS_BATCH_SIZE]
        query = f"bibcode:({' OR '.join(batch)})"
        params = {
            "q":    query,
            "fl":   "bibcode,title,author,year,pub,abstract,doi,identifier,citation_count,reference,citation,adsurl",
            "rows": len(batch),
        }
        resp = requests.get(ADS_SEARCH_URL, headers=_ads_headers(token), params=params, timeout=30)
        if resp.status_code == 200:
            results.extend(resp.json().get("response", {}).get("docs", []))
        # polite pause between batches
        if i + ADS_BATCH_SIZE < len(bibcodes):
            time.sleep(1)
    return results


def _fetch_ads_bibtex(bibcodes: list[str], token: str) -> dict[str, str]:
    """Fetch BibTeX for a list of bibcodes. Returns {bibcode: bibtex_string}."""
    bibtex_map = {}
    for i in range(0, len(bibcodes), ADS_BATCH_SIZE):
        batch = bibcodes[i:i + ADS_BATCH_SIZE]
        resp = requests.post(
            ADS_BIBTEX_URL,
            headers=_ads_headers(token),
            json={"bibcode": batch},
            timeout=30,
        )
        if resp.status_code == 200:
            raw = resp.json().get("export", "")
            # Split the combined BibTeX blob into individual entries
            for entry in re.split(r'(?=@\w+\{)', raw):
                entry = entry.strip()
                if not entry:
                    continue
                m = re.match(r'@\w+\{([^,]+),', entry)
                if m:
                    bibtex_map[m.group(1)] = entry   # key is the ADS bibcode
        if i + ADS_BATCH_SIZE < len(bibcodes):
            time.sleep(1)
    return bibtex_map


def _get_or_create_satellite(doc: dict, bibtex_map: dict) -> Paper | None:
    """Given one ADS doc dict, get existing Paper or create a non-core satellite."""
    bibcode = doc.get("bibcode")
    if not bibcode:
        return None

    # 1. already in DB?
    existing = Paper.objects.filter(bibcode=bibcode).first()
    if existing:
        # keep existing core status; just refresh abstract if missing
        if not existing.abstract and doc.get("abstract"):
            existing.abstract = doc["abstract"]
            existing.save(update_fields=["abstract"])
        return existing

    # 2. build author string from ADS list
    authors_list = doc.get("author", [])
    if not authors_list:
        return None
    authors_str = " and ".join(authors_list)

    # 3. parse year
    try:
        year = int(doc.get("year", 0))
    except (ValueError, TypeError):
        return None

    # 4. generate local key
    key = generate_identifier(first_author=authors_str, year=year)

    # 5. build adsurl
    adsurl = doc.get("adsurl") or f"https://ui.adsabs.harvard.edu/abs/{bibcode}"

    # 6. doi / arxiv from identifier list
    doi    = None
    arxiv  = None
    for ident in doc.get("identifier", []):
        if ident.startswith("10.") and not doi:
            doi = ident
        if ident.startswith("arXiv:") and not arxiv:
            arxiv = f"https://arxiv.org/abs/{ident[6:]}"

    # bibtex string (may be absent if ADS export didn't include it)
    bibtex_str = bibtex_map.get(bibcode, "")

    title_list = doc.get("title", [])
    title = title_list[0] if title_list else None

    paper = Paper.objects.create(
        key      = key,
        bibcode  = bibcode,
        title    = title,
        authors  = authors_str,
        year     = year,
        journal  = doc.get("pub", None),
        doi      = doi,
        adsurl   = adsurl,
        arxiv    = arxiv,
        bibtex   = bibtex_str,
        abstract = doc.get("abstract", None),
        core     = False,
        ads_citation_count = doc.get("citation_count", None),
    )
    return paper


# ---------------------------------------------------------------------------
# Main public function: fetch_and_update_from_ads
# ---------------------------------------------------------------------------

def fetch_and_update_from_ads(paper: Paper) -> dict:
    """
    Full ADS update for a single core paper:
      1. Fetch extended metadata for the paper itself.
      2. Collect all reference + citation bibcodes.
      3. Bulk-fetch metadata + BibTeX for all satellite bibcodes.
      4. Create non-core Paper objects for any not yet in DB.
      5. Link them via paper.references / paper.citing_papers M2M.
      6. Update paper.ads_citation_count, paper.last_ads_updated, paper.abstract.

    Returns a summary dict with counts.
    """
    token = _get_ads_token()

    if not paper.bibcode:
        return {"error": "Paper has no bibcode — cannot query ADS."}

    # ── Step 1: fetch metadata for the paper itself ──────────────────────────
    main_docs = _fetch_ads_metadata([paper.bibcode], token)
    if not main_docs:
        return {"error": f"ADS returned no results for bibcode {paper.bibcode}"}

    main_doc = main_docs[0]

    # Update core paper fields
    update_fields = ["last_ads_updated", "ads_citation_count"]
    paper.last_ads_updated   = timezone.now()
    paper.ads_citation_count = main_doc.get("citation_count", paper.ads_citation_count)

    if not paper.abstract and main_doc.get("abstract"):
        paper.abstract = main_doc["abstract"]
        update_fields.append("abstract")

    # Backfill bibcode if somehow missing
    if not paper.bibcode:
        paper.bibcode = main_doc.get("bibcode")
        update_fields.append("bibcode")

    paper.save(update_fields=update_fields)

    # ── Step 2: collect satellite bibcodes ───────────────────────────────────
    ref_bibcodes  = main_doc.get("reference", [])   # papers this paper cites
    cite_bibcodes = main_doc.get("citation",  [])   # papers that cite this paper

    all_satellite_bibcodes = list(set(ref_bibcodes + cite_bibcodes))

    summary = {
        "references_total":  len(ref_bibcodes),
        "citations_total":   len(cite_bibcodes),
        "satellite_new":     0,
        "satellite_updated": 0,
    }

    if not all_satellite_bibcodes:
        return summary

    # ── Step 3: bulk metadata + BibTeX for satellites ────────────────────────
    satellite_docs   = _fetch_ads_metadata(all_satellite_bibcodes, token)
    satellite_bibtex = _fetch_ads_bibtex(all_satellite_bibcodes, token)

    doc_map = {d["bibcode"]: d for d in satellite_docs}

    # ── Step 4 & 5: create/get satellite papers and link M2M ─────────────────
    ref_papers  = []
    cite_papers = []

    for bc in ref_bibcodes:
        doc = doc_map.get(bc)
        if not doc:
            continue
        already_existed = Paper.objects.filter(bibcode=bc).exists()
        sat = _get_or_create_satellite(doc, satellite_bibtex)
        if sat:
            ref_papers.append(sat)
            if already_existed:
                summary["satellite_updated"] += 1
            else:
                summary["satellite_new"] += 1

    for bc in cite_bibcodes:
        doc = doc_map.get(bc)
        if not doc:
            continue
        already_existed = Paper.objects.filter(bibcode=bc).exists()
        sat = _get_or_create_satellite(doc, satellite_bibtex)
        if sat:
            cite_papers.append(sat)
            if already_existed:
                summary["satellite_updated"] += 1
            else:
                summary["satellite_new"] += 1

    # Set M2M relationships (add, don't replace, so existing links survive)
    paper.references.add(*ref_papers)
    # Store papers that cite this paper on the explicit papers_cited_by field
    paper.papers_cited_by.add(*cite_papers)

    # Also link from the satellite side: each citing paper has this paper in its references
    for sat in cite_papers:
        sat.references.add(paper)

    return summary
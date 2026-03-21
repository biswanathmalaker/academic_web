import re
from .models import Paper

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


def extract_metadata(entry: str):
    """Parse a BibTeX entry into structured metadata."""
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode  # fixes encoding & makes text cleaner
    
    bib_database = bibtexparser.loads(entry, parser=parser)
    if not bib_database.entries:
        return {}
    
    entry = bib_database.entries[0]

    # Safely extract fields
    key = entry.get("ID", "Unknown Key")
    title = entry.get("title", "Unknown Title")
    authors = entry.get("author", "Unknown Author")
    year = entry.get("year", None)
    journal = entry.get("journal", "Unknown Journal")
    volume = entry.get("volume", None)
    pages = entry.get("pages", None)
    eid = entry.get("eid", None)
    doi = entry.get("doi", None)
    adsurl = entry.get("adsurl", None)
    arxiv = entry.get("eprint", None)

    data = {
        "key": key,
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "volume": volume,
        "pages": pages,
        "eid": eid,
        "doi": doi,
        "adsurl": adsurl,
        "arxiv": f"https://arxiv.org/abs/{arxiv}" if arxiv else None,
    }

    # Clean journal string
    if data["journal"]:
        data["journal"] = (
            data["journal"].encode("utf-8", "ignore").decode("utf-8").replace("\x07", "A")
        )

    return data


def generate_identifier(first_author: str, year: int, exclude_pk=None) -> str:
    """
    Generate a unique key like:
    weitz-2025, weitz-2025a, weitz-2025b, ...
    """
    if not first_author or not year:
        return "unknown"

    base = re.sub(r'[^a-z]', '', first_author.split(",")[0].lower())
    base_key = f"{base}-{year}"

    qs = Paper.objects.filter(key__startswith=base_key)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    existing = set(qs.values_list("key", flat=True))

    if base_key not in existing:
        return base_key

    # add suffixes a, b, c...
    suffix = ord("a")
    while True:
        candidate = f"{base_key}{chr(suffix)}"
        if candidate not in existing:
            return candidate
        suffix += 1


def save_bibtex(bibtex_entry: str):
    """Create or update Paper entry in DB and assign unique key.
       Skip if same author+volume+pages already exists.
    """
    data = extract_metadata(bibtex_entry)

    # Add raw bibtex
    data["bibtex"] = bibtex_entry

    # Ensure year is integer
    if data["year"]:
        try:
            data["year"] = int(data["year"])
        except ValueError:
            data["year"] = None

    # Check duplicates: same author + volume + pages
    existing = Paper.objects.filter(
        authors=data.get("authors"),
        volume=data.get("volume"),
        pages=data.get("pages"),
    ).first()

    if existing:
        return existing  # Do not create duplicate

    # Generate unique key based on author+year
    identifier = generate_identifier(
        first_author=data.get("authors", "unknown"),
        year=data.get("year"),
    )
    data["key"] = identifier

    # Save or update
    paper, _ = Paper.objects.update_or_create(
        key=data["key"],
        defaults=data,
    )

    return paper

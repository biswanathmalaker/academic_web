from datetime import datetime, timedelta, timezone
import arxiv
from .models import ArxivPaper, SyncLog

def sync_stellar_papers(force=False):
    now = datetime.now(timezone.utc)
    
    # 1. Weekend Logic
    if not force and now.weekday() in [5, 6]:
        return "Skipped: Weekend"

    # 2. Get the last successful sync time
    last_log = SyncLog.objects.order_by('-last_sync').first()
    
    if last_log:
        # If forced, we ignore the 24h throttle, but we still use the timestamp 
        # to know how far back to fetch.
        if not force and (now - last_log.last_sync) < timedelta(days=1):
            return "Skipped: Recently Updated"
        
        # This is the "start date" for our fetch
        since_date = last_log.last_sync
    else:
        # Fallback for the very first sync
        since_date = now - timedelta(days=7)

    client = arxiv.Client()
    # Increase max_results slightly just in case there's a backlog
    search = arxiv.Search(
        query="cat:astro-ph.SR",
        max_results=100, 
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    papers_added = 0
    results = client.results(search)

    for result in results:
        # ArXiv 'published' is usually UTC aware. 
        # If the paper is older than our last sync, we stop.
        if result.published <= since_date:
            break
        
        obj, created = ArxivPaper.objects.update_or_create(
            arxiv_id=result.entry_id,
            defaults={
                'title': result.title,
                'summary': result.summary,
                'authors': ", ".join(a.name for a in result.authors),
                'published_date': result.published,
                'pdf_url': result.pdf_url,
            }
        )
        if created: 
            papers_added += 1

    # 3. Create a new log entry to mark this point in time
    SyncLog.objects.create(status=f"Added {papers_added} papers")
    return f"Success: {papers_added} added since {since_date.strftime('%Y-%m-%d %H:%M')}"
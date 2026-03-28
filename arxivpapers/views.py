from django.shortcuts import render
from django_q.tasks import async_task
from .models import ArxivPaper
from .services import sync_stellar_papers

def paper_list_view(request):
    # Trigger background auto-sync on page load
    async_task('arxivpapers.services.sync_stellar_papers')
    
    papers = ArxivPaper.objects.all()[:20]
    return render(request, 'arxivpapers/papers.html', {'papers': papers})

def manual_sync_view(request):
    # Manual trigger bypasses the 24h/weekend check
    sync_stellar_papers(force=True)
    
    papers = ArxivPaper.objects.all()[:20]
    return render(request, 'arxivpapers/papers.html', {'papers': papers})
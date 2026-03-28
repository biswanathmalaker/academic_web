from django.db import models

class ArxivPaper(models.Model):
    arxiv_id = models.CharField(max_length=100, unique=True)
    title = models.TextField()
    summary = models.TextField()
    authors = models.TextField()  # Stored as a comma-separated string
    published_date = models.DateTimeField()
    pdf_url = models.URLField()

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

class SyncLog(models.Model):
    last_sync = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="Success")

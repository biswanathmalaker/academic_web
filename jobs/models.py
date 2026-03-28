from django.db import models

class PostdocPosition(models.Model):
    title = models.CharField(max_length=300)
    institution = models.CharField(max_length=255, blank=True)
    job_url = models.URLField(verbose_name="Job Advertisement URL")
    deadline = models.DateField(null=True, blank=True)
    
    # Optional metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.institution}"

    class Meta:
        # Default ordering: closest deadlines first. 
        # Null deadlines will usually appear last.
        ordering = ['deadline']
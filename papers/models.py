import re
from django.db import models


class Category(models.Model):
    """
    Broader classifications like: Flares, Jets, Nebula, Star_Formation.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True) # Useful for clean Web URLs

    def __str__(self):
        return self.name
    
    
class Paper(models.Model):
    key = models.CharField(max_length=100, unique=True)   # BibTeX/citation key
    title = models.TextField(blank=True, null=True)
    authors = models.TextField()
    year = models.IntegerField()
    journal = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=20, blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True)
    eid = models.CharField(max_length=50, blank=True, null=True)
    
    doi = models.URLField(blank=True, null=True)
    adsurl = models.URLField(blank=True, null=True)
    arxiv = models.URLField(blank=True, null=True)
    bibtex = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    abstract_note_AI = models.TextField(blank=True, null=True)

    categories = models.ManyToManyField(
            Category, 
            blank=True, 
            related_name='papers'
        )

    def generate_key(self):
        """
        Generate a unique citation key like:
        weitz-2025, weitz-2025a, weitz-2025b, etc.
        """
        # get first author's last name, lowercase
        first_author = self.authors.split(",")[0].strip()
        base = re.sub(r'[^a-z]', '', first_author.lower())  # keep only a–z

        # base key with year
        key_base = f"{base}-{self.year}"

        # check if already exists in DB
        existing_keys = (
            Paper.objects.filter(key__startswith=key_base)
            .exclude(pk=self.pk)
            .values_list("key", flat=True)
        )

        if key_base not in existing_keys:
            return key_base

        # suffix letters a, b, c...
        suffix = ord("a")
        while True:
            candidate = f"{key_base}{chr(suffix)}"
            if candidate not in existing_keys:
                return candidate
            suffix += 1

    def save(self, *args, **kwargs):
        if not self.key:  # only assign if not already set
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def citation(self):
        """
        Return citation string for in-text use.
        Example: (Weitz 2025), (Weitz 2025a), etc.
        """
        first_author = self.authors.split(",")[0].strip().split()[-1]
        return f"{first_author} {self.year}{self.key.replace(f'{first_author.lower()}-{self.year}', '')}"
    
    def __str__(self):
        return self.generate_key()



# papers/models.py

SECTION_CHOICES = [
    ('abstract','Abstract'),
    ('introductions', 'Introduction'),
    ('methods', 'Methods'),
    ('results', 'Results'),
    ('discussion', 'Discussion'),
    ('conclusion', 'Conclusion'),
]





class Section(models.Model):
    name = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



    
class Statement(models.Model):
    paper = models.ForeignKey('Paper', on_delete=models.CASCADE, related_name='statements')
    section = models.CharField(max_length=50, choices=SECTION_CHOICES,default='abstract')

    topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='statements'
    )

    
    text = models.TextField()
    
    citations = models.ManyToManyField('Paper', blank=True, related_name='cited_by')
    
    page_number = models.CharField(max_length=50, blank=True)


    def __str__(self):
        return f"{self.get_section_display()} | {self.topic}: {self.text[:40]}"

    





    
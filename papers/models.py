import re
from django.db import models


class Category(models.Model):
    """
    Broader classifications like: Flares, Jets, Nebula, Star_Formation.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name


class Paper(models.Model):
    key        = models.CharField(max_length=100, unique=True)   # BibTeX/citation key
    bibcode    = models.CharField(max_length=100, unique=True, null=True, blank=True)  # ADS bibcode e.g. 2023ApJ...951L..15K

    title      = models.TextField(blank=True, null=True)
    authors    = models.TextField()
    year       = models.IntegerField()
    journal    = models.CharField(max_length=50, blank=True, null=True)
    volume     = models.CharField(max_length=20, blank=True, null=True)
    pages      = models.CharField(max_length=50, blank=True, null=True)
    eid        = models.CharField(max_length=50, blank=True, null=True)

    doi        = models.URLField(blank=True, null=True)
    adsurl     = models.URLField(blank=True, null=True)
    arxiv      = models.URLField(blank=True, null=True)
    bibtex     = models.TextField(blank=True, null=True)
    abstract   = models.TextField(blank=True, null=True)
    abstract_note_AI = models.TextField(blank=True, null=True)

    # ── new fields ──────────────────────────────────────────────────────────────
    core = models.BooleanField(
        default=True,
        help_text="True = manually added paper; False = satellite paper pulled in via ADS references/citations"
    )
    last_ads_updated = models.DateTimeField(
        null=True, blank=True,
        help_text="Last time ADS metadata was fetched for this paper"
    )
    ads_citation_count = models.IntegerField(
        null=True, blank=True,
        help_text="Global citation count from ADS (not just papers in this DB)"
    )

    # Self-referential M2M: paper.references.all()  → papers this paper cites
    #                        paper.citing_papers.all() → papers that cite this paper

    # Papers this paper cites (from ADS reference list)
    references = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='cited_by_papers',
        help_text="Papers cited by this paper"
    )

    # Papers that cite this paper (from ADS citation list)
    papers_cited_by = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='cites_papers',
        help_text="Papers that cite this paper, as fetched from ADS"
    )
    
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='papers'
    )

    # ── helpers ─────────────────────────────────────────────────────────────────

    # @property
    # def local_citation_count(self):
    #     """How many core/satellite papers in this DB cite this paper."""
    #     return self.citing_papers.count()
    
    @property
    def local_citation_count(self):
        return self.papers_cited_by.count()

    def generate_key(self):
        """
        Generate a unique citation key like:
        weitz-2025, weitz-2025a, weitz-2025b, etc.
        """
        first_author = self.authors.split(",")[0].strip()
        base = re.sub(r'[^a-z]', '', first_author.lower())
        key_base = f"{base}-{self.year}"

        existing_keys = (
            Paper.objects.filter(key__startswith=key_base)
            .exclude(pk=self.pk)
            .values_list("key", flat=True)
        )

        if key_base not in existing_keys:
            return key_base

        suffix = ord("a")
        while True:
            candidate = f"{key_base}{chr(suffix)}"
            if candidate not in existing_keys:
                return candidate
            suffix += 1

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def citation(self):
        first_author = self.authors.split(",")[0].strip().split()[-1]
        return f"{first_author} {self.year}{self.key.replace(f'{first_author.lower()}-{self.year}', '')}"

    def __str__(self):
        return self.generate_key()


# ── Section / Topic / Statement ──────────────────────────────────────────────

SECTION_CHOICES = [
    ('abstract',      'Abstract'),
    ('introductions', 'Introduction'),
    ('methods',       'Methods'),
    ('results',       'Results'),
    ('discussion',    'Discussion'),
    ('conclusion',    'Conclusion'),
]


class Section(models.Model):
    name = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Topic(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Statement(models.Model):
    paper   = models.ForeignKey('Paper', on_delete=models.CASCADE, related_name='statements')
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, default='abstract')

    topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='statements'
    )

    text        = models.TextField()
    citations   = models.ManyToManyField('Paper', blank=True, related_name='cited_by')
    page_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.get_section_display()} | {self.topic}: {self.text[:40]}"
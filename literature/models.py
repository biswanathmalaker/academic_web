from django.db import models

class Book(models.Model):
    book_name = models.CharField(max_length=255)
    preface = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.book_name



class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    chapter_name = models.CharField(max_length=200)
    chapter_introduction = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.book.book_name} - {self.chapter_name}"


class Section(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='sections', on_delete=models.CASCADE)
    section_name = models.CharField(max_length=200)
    section_introduction = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.chapter.chapter_name} - {self.section_name}"


class Subsection(models.Model):
    section = models.ForeignKey(Section, related_name='subsections', on_delete=models.CASCADE)
    subsection_name = models.CharField(max_length=200)
    subsection_introduction = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.section.section_name} - {self.subsection_name}"


class SubSubsection(models.Model):
    subsection = models.ForeignKey(Subsection, related_name='subsubsections', on_delete=models.CASCADE)
    subsubsection_name = models.CharField(max_length=200)
    subsubsection_introduction = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.subsection.subsection_name} - {self.subsubsection_name}"


class Code(models.Model):
    # Generic foreign keys to allow code to be attached to any level
    chapter = models.ForeignKey(Chapter, related_name='codes', on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, related_name='codes', on_delete=models.CASCADE, null=True, blank=True)
    subsection = models.ForeignKey(Subsection, related_name='codes', on_delete=models.CASCADE, null=True, blank=True)
    subsubsection = models.ForeignKey(SubSubsection, related_name='codes', on_delete=models.CASCADE, null=True, blank=True)
    
    file_name = models.CharField(max_length=200)
    code_content = models.TextField()
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        parent = self.subsubsection or self.subsection or self.section or self.chapter
        return f"{parent} - {self.file_name}"

    def get_parent(self):
        """Return the parent object (chapter, section, subsection, or subsubsection)"""
        if self.subsubsection:
            return self.subsubsection
        elif self.subsection:
            return self.subsection
        elif self.section:
            return self.section
        elif self.chapter:
            return self.chapter
        return None
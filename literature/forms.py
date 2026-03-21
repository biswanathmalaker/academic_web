from django import forms
from .models import Book, Chapter, Section, Subsection, SubSubsection, Code

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_name', 'preface']


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['book', 'chapter_name', 'chapter_introduction']


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['chapter', 'section_name', 'section_introduction']


class SubsectionForm(forms.ModelForm):
    class Meta:
        model = Subsection
        fields = ['section', 'subsection_name', 'subsection_introduction']


class SubSubsectionForm(forms.ModelForm):
    class Meta:
        model = SubSubsection
        fields = ['subsection', 'subsubsection_name', 'subsubsection_introduction']


class CodeForm(forms.ModelForm):
    class Meta:
        model = Code
        fields = ['file_name', 'code_content', 'description']
        widgets = {
            'code_content': forms.Textarea(attrs={'rows': 20, 'style': 'font-family: monospace;'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
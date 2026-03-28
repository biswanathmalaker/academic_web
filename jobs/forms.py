        
from django import forms
from .models import PostdocPosition

class PostdocPositionForm(forms.ModelForm):
    class Meta:
        model = PostdocPosition
        fields = ['title', 'institution', 'job_url', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
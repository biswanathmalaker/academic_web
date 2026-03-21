from django import forms
from .models import Statement, Paper, SECTION_CHOICES

# papers/forms.py

from django import forms
from .models import Statement, Paper

class StatementForm(forms.ModelForm):
    class Meta:
        model = Statement
        fields = "__all__"
        widgets = {
            "citations": forms.SelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["citations"].queryset = Paper.objects.order_by("-year")

        self.fields["citations"].label_from_instance = (
            lambda obj: f"{obj.key} — {obj.title or 'No title'}"
        )


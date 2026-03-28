from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import PostdocPosition
from .forms import PostdocPositionForm
from django.utils import timezone

class PositionListView(ListView):
    model = PostdocPosition
    template_name = 'jobs/job_list.html'
    context_object_name = 'positions'

    def get_queryset(self):
        return PostdocPosition.objects.all().order_by('deadline')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context

class PositionCreateView(CreateView):
    model = PostdocPosition
    form_class = PostdocPositionForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:position_list')
    
    
def DashboardView(request):
    return render(request, 'jobs/dashboard.html')
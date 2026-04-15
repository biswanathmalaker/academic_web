from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Paper, Category
from .utils import save_bibtex
# views.py
import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404, redirect,render
from django.views.decorators.http import require_POST
from .models import Paper , Section , Statement
from django.shortcuts import render, get_object_or_404, redirect
from .models import Paper, Statement
from .forms import StatementForm, SECTION_CHOICES

from django.views.decorators.http import require_http_methods


from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


from django.shortcuts import render, redirect, get_object_or_404
from .models import Statement
from .forms import StatementForm

# def index(request):
#     papers = Paper.objects.all().order_by("-year")
#     return render(request, "papers/index.html", {"papers": papers})

import os
from django.conf import settings
from django.shortcuts import render
from .models import Paper


import os
from django.conf import settings
from django.shortcuts import render
from .models import Paper

def get_filtered_papers(request):
    filter_option = request.GET.get("filter")
    if filter_option:
        request.session["papers_filter"] = filter_option
    else:
        filter_option = request.session.get("papers_filter", "all_papers")

    form_name = request.GET.get("form_name")
    if form_name == "category_filter":
        category_filter = request.GET.getlist("category")
        request.session["category_filter"] = category_filter
    else:
        category_filter = request.session.get("category_filter", [])

    papers = Paper.objects.all().order_by("-year")
    pdf_dir = os.path.join(settings.BASE_DIR, "papers", "pdf")

    if filter_option == "only_pdf_available":
        papers = [p for p in papers if os.path.exists(os.path.join(pdf_dir, f"{p.key}.pdf"))]
    elif filter_option == "only_non_pdf":
        papers = [p for p in papers if not os.path.exists(os.path.join(pdf_dir, f"{p.key}.pdf"))]
    elif filter_option == "papers_cited_by_statements":
        papers = (
            Paper.objects
            .filter(cited_by__isnull=False)
            .distinct()
            .order_by("-year")
        )

    if category_filter:
        papers = [p for p in papers if p.categories.filter(id__in=category_filter).exists()]

    return papers, filter_option, category_filter


def index(request):
    papers, filter_option, category_filter = get_filtered_papers(request)
    categories = Category.objects.all()
    return render(
        request,
        "papers/index.html",
        {
            "papers": papers,
            "filter_option": filter_option,
            "categories": categories,
            "category_filter": category_filter,
        }
    )

@require_POST
def update_categories(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    category_ids = request.POST.getlist('categories')
    paper.categories.set(category_ids)
    return redirect('papers:index')

def add_paper(request):
    if request.method == "POST":
        bibtex_entry = request.POST.get("bibtex")
        if bibtex_entry:
            save_bibtex(bibtex_entry)
        return redirect("papers:index")
    return render(request, "papers/add_paper.html")



# @require_POST
# def fetch_abstract(request, pk):
#     paper = get_object_or_404(Paper, pk=pk)
#     if paper.adsurl:
#         abs_url = paper.adsurl.rstrip("/") + "/abstract"
#         resp = requests.get(abs_url)
#         if resp.ok:
#             soup = BeautifulSoup(resp.text, "html.parser")
#             abs_div = soup.find("div", class_="s-abstract-text")
#             if abs_div:
#                 paper.abstract = abs_div.get_text(strip=True)
#                 paper.save()

#     # re-render the same page (index.html) with updated papers
#     papers = Paper.objects.all().order_by("year")
#     return render(request, "papers/index.html", {"papers": papers})

@require_POST
def fetch_abstract(request, paper_id):
    paper = get_object_or_404(Paper, pk=paper_id)
    if paper.adsurl:
        url = paper.adsurl.rstrip("/") + "/abstract"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            abs_div = soup.find("div", class_="s-abstract-text")
            if abs_div:
                abs_text = abs_div.get_text(" ", strip=True).replace("Abstract", "", 1).strip()
                paper.abstract = abs_text
                paper.save()
                
    papers = Paper.objects.all().order_by("-year")
    return redirect("papers:index")
    # Papers_selected = []
    # for paper in papers:
    #     if paper.abstract == None:
    #         Papers_selected.append(paper)
    # print(f"{len(Papers_selected)} of {len(papers)} fetched!")
    # return render(request, "papers/index.html", {"papers": papers})






def statement_create(request):
    if request.method == 'POST':
        form = StatementForm(request.POST)
        if form.is_valid():
            statement = form.save()
            # Remember the section the user picked
            request.session['last_section'] = statement.section
            return redirect('statement_list')  # or wherever you list statements
    else:
        # Pre-fill section with last selected
        last = request.session.get('last_section')
        form = StatementForm(initial={'section': last} if last else None)
    return render(request, 'statement_form.html', {'form': form})

# def statement_list(request):
#     # Filter list based on last selected section (optional)
#     last = request.session.get('last_section')
#     statements = Statement.objects.all()
#     return render(request, 'statement_list.html', {
#         'statements': statements,
#         'last_section': last
#     })


# papers/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Paper, Statement
from .forms import StatementForm

def manage_notes(request, paper_id):
    paper = get_object_or_404(Paper, pk=paper_id)

    statement_id = request.GET.get("statement")
    statement = None

    if statement_id:
        statement = get_object_or_404(
            Statement,
            pk=statement_id,
            paper=paper
        )

    if request.method == "POST":
        form = StatementForm(request.POST, instance=statement)
        if form.is_valid():
            stmt = form.save(commit=False)
            stmt.paper = paper
            stmt.save()
            form.save_m2m()
            return redirect(
                f"{request.path}?statement={stmt.id}"
            )
    else:
        form = StatementForm(instance=statement)

    grouped = {}
    for s in paper.statements.prefetch_related("citations"):
        grouped.setdefault(s.get_section_display(), []).append(s)

    return render(request, "papers/manage_notes.html", {
        "paper": paper,
        "form": form,
        "statements": grouped,
        "editing_statement": statement,
    })




def read_notes(request, paper_id):
    paper = get_object_or_404(Paper, pk=paper_id)



    # Group existing statements by section name
    grouped = {}
    for s in paper.statements.prefetch_related('citations'):
        grouped.setdefault(s.get_section_display(), []).append(s)

    return render(request, "papers/read_notes.html", {
        "paper": paper,
        "statements": grouped,
        "section_choices": SECTION_CHOICES,
    })
    
    

def statement_update(request, pk):
    stmt = get_object_or_404(Statement, pk=pk)
    if request.method == 'POST':
        form = StatementForm(request.POST, instance=stmt)
        if form.is_valid():
            stmt = form.save()
            # Remember last section again if changed
            request.session['last_section'] = stmt.section
            return redirect('statement_list')
    else:
        form = StatementForm(instance=stmt)
    return render(request, 'papers/statement_form.html', {'form': form})

def statement_delete(request, pk):
    stmt = get_object_or_404(Statement, pk=pk)
    if request.method == 'POST':
        stmt.delete()
        return redirect('statement_list')
    return render(request, 'papers/confirm_delete.html', {'statement': stmt})



@require_http_methods(["POST"])
def add_abstract(request, paper_id):
    paper = get_object_or_404(Paper, pk=paper_id)
    abstract_text = request.POST.get("abstract")
    if abstract_text:
        paper.abstract = abstract_text.strip()
        paper.save()
    return redirect("papers:index")





# views.py
# import os
# from django.http import FileResponse, Http404
# from django.shortcuts import get_object_or_404
# from TTS.api import TTS
# from .models import Paper

# AUDIO_DIR = "./papers/audio/abstract/"
# os.makedirs(AUDIO_DIR, exist_ok=True)

# # Load Coqui TTS model once
# model_names = ["tts_models/en/ljspeech/tacotron2-DDC","tts_models/en/vctk/vits"]
# model_name = model_names[0]
# # tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
# tts = TTS(model_name=model_name, progress_bar=False, gpu=False)



# def get_paper_audio(request, paper_key):
#     # Fetch the paper object
#     paper = get_object_or_404(Paper, key=paper_key)
    
#     # Determine audio file path
#     audio_path = os.path.join(AUDIO_DIR, f"{paper_key}.mp3")

#     # Generate audio if it doesn't exist
#     if not os.path.exists(audio_path):
#         text_to_speak = paper.abstract or "No abstract available."
#         if model_name == model_names[0]:
#             tts.tts_to_file(
#                     text=text_to_speak,
#                     file_path=audio_path,
#                     # emotion="neutral" # optional if model supports emotions
#                 )
#         elif model_name == model_names[1]:
#             tts.tts_to_file(
#                 text=text_to_speak,
#                 file_path=audio_path,
#                 speaker="p225",   # example voice
#                 # emotion="neutral" # optional if model supports emotions
#             )

#     # Serve the audio file
#     if os.path.exists(audio_path):
#         return FileResponse(open(audio_path, "rb"), content_type="audio/mpeg")
#     else:
#         raise Http404("Audio could not be generated")






def all_papers_detail(request):
    papers, _, _ = get_filtered_papers(request)
    return render(request, "papers/all_papers_detail.html", {"papers": papers})


def all_papers_pdf(request):
    papers, _, _ = get_filtered_papers(request)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for i, paper in enumerate(papers, 1):
        story.append(Paragraph(f"{i}. {paper.title or '(No Title)'}", styles['Title']))
        story.append(Paragraph(f"Authors: {paper.authors}", styles['Normal']))
        story.append(Paragraph(f"Year: {paper.year}", styles['Normal']))
        if paper.journal:
            story.append(Paragraph(f"Journal: {paper.journal}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Abstract: {paper.abstract or 'No abstract available.'}", styles['Normal']))
        story.append(Spacer(1, 18))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_papers.pdf"'
    response.write(pdf)
    return response




# papers/views.py

from django.shortcuts import render
from .models import Statement, Topic

def statement_list(request):
    topics = Topic.objects.all().order_by("name")

    selected_topics = request.GET.getlist("topics")

    statements = (
        Statement.objects
        .select_related("paper", "topic")
        .prefetch_related("citations")
        .order_by("paper__year")
    )

    if selected_topics:
        statements = statements.filter(topic__id__in=selected_topics)

    context = {
        "statements": statements,
        "topics": topics,
        "selected_topics": list(map(int, selected_topics)) if selected_topics else [],
    }
    return render(request, "papers/statement_list.html", context)




# papers/views.py

from django.shortcuts import render
from .models import Statement, Topic

def statements_by_topic(request):
    topics = (
        Topic.objects
        .prefetch_related(
            "statements__paper",
            "statements__citations"
        )
        .order_by("name")
    )

    # Sort statements per topic (year → paper → section)
    for topic in topics:
        topic.sorted_statements = (
            topic.statements
            .select_related("paper")
            .order_by(
                "paper__year",
                "paper__key",
                "section"
            )
        )

    return render(
        request,
        "papers/statements_by_topic.html",
        {"topics": topics}
    )



# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Paper, Section, Subsection, Statement
# from .forms import SectionForm, SubsectionForm, StatementForm  # create these ModelForms

# def manage_notes(request, paper_id):
    # paper = get_object_or_404(Paper, pk=paper_id)
    # sections = paper.sections.all().order_by('order')

    # # Handle new section
    # if request.method == 'POST' and 'new_section' in request.POST:
    #     section_form = SectionForm(request.POST)
    #     if section_form.is_valid():
    #         sec = section_form.save(commit=False)
    #         sec.paper = paper
    #         sec.save()
    #         return redirect('papers:manage_notes', paper_id=paper.id)
    # else:
    #     section_form = SectionForm()

    # return render(
    #     request, 
    #     'papers/manage_notes.html',
    #     {
    #         'paper': paper,
    #         'sections': sections,
    #         'section_form': section_form,
    #     }
    # )
    
    # return render(
    #     request, 
    #     'papers/manage_notes.html',
    #     {
    #     }
    # )


# def delete_section(request, paper_id, pk):
#     section = get_object_or_404(Section, pk=pk, paper_id=paper_id)
#     section.delete()
#     return redirect('papers:manage_notes', paper_id=paper_id)

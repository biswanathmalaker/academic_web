from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Book, Chapter, Section, Subsection, SubSubsection, Code, Note, NoteImage
from .forms import BookForm, ChapterForm, SectionForm, SubsectionForm, SubSubsectionForm, CodeForm, NoteForm


def index(request):
    books = Book.objects.prefetch_related(
        'chapters__notes',
        'chapters__sections__notes',
        'chapters__sections__subsections__notes',
        'chapters__sections__subsections__subsubsections__notes',
    ).all().order_by('order')
    return render(request, 'literature/index.html', {'books': books})


# ----- Book -----
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = BookForm()
    return render(request, 'literature/form.html', {'form': form, 'title': 'Add Book'})

def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = BookForm(instance=book)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit Book'})

def delete_book(request, pk):
    get_object_or_404(Book, pk=pk).delete()
    return redirect('literature:index')


# ----- Chapter -----
def add_chapter(request):
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        book_id = request.GET.get('book')
        if book_id:
            form = ChapterForm(initial={'book': book_id})
        else:
            form = ChapterForm()
    return render(request, 'literature/form.html', {'form': form, 'title': 'Add Chapter'})

def update_chapter(request, pk):
    chapter = get_object_or_404(Chapter, pk=pk)
    if request.method == "POST":
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = ChapterForm(instance=chapter)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit Chapter'})

def delete_chapter(request, pk):
    get_object_or_404(Chapter, pk=pk).delete()
    return redirect('literature:index')


# ----- Section -----
def add_section(request):
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        chapter_id = request.GET.get('chapter')
        if chapter_id:
            form = SectionForm(initial={'chapter': chapter_id})
        else:
            form = SectionForm()
    return render(request, 'literature/form.html', {'form': form, 'title': 'Add Section'})

def update_section(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = SectionForm(instance=section)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit Section'})

def delete_section(request, pk):
    get_object_or_404(Section, pk=pk).delete()
    return redirect('literature:index')


# ----- Subsection -----
def add_subsection(request):
    if request.method == "POST":
        form = SubsectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        section_id = request.GET.get('section')
        if section_id:
            form = SubsectionForm(initial={'section': section_id})
        else:
            form = SubsectionForm()
    return render(request, 'literature/form.html', {'form': form, 'title': 'Add Subsection'})

def update_subsection(request, pk):
    subsection = get_object_or_404(Subsection, pk=pk)
    if request.method == "POST":
        form = SubsectionForm(request.POST, instance=subsection)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = SubsectionForm(instance=subsection)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit Subsection'})

def delete_subsection(request, pk):
    get_object_or_404(Subsection, pk=pk).delete()
    return redirect('literature:index')


# ----- SubSubsection -----
def add_subsubsection(request):
    if request.method == "POST":
        form = SubSubsectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        subsection_id = request.GET.get('subsection')
        if subsection_id:
            form = SubSubsectionForm(initial={'subsection': subsection_id})
        else:
            form = SubSubsectionForm()
    return render(request, 'literature/form.html', {'form': form, 'title': 'Add SubSubsection'})

def update_subsubsection(request, pk):
    subsubsection = get_object_or_404(SubSubsection, pk=pk)
    if request.method == "POST":
        form = SubSubsectionForm(request.POST, instance=subsubsection)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = SubSubsectionForm(instance=subsubsection)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit SubSubsection'})

def delete_subsubsection(request, pk):
    get_object_or_404(SubSubsection, pk=pk).delete()
    return redirect('literature:index')


# ----- Code -----
def add_code(request):
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.save(commit=False)
            chapter_id = request.POST.get('chapter_id')
            section_id = request.POST.get('section_id')
            subsection_id = request.POST.get('subsection_id')
            subsubsection_id = request.POST.get('subsubsection_id')
            if subsubsection_id:
                code.subsubsection_id = subsubsection_id
            elif subsection_id:
                code.subsection_id = subsection_id
            elif section_id:
                code.section_id = section_id
            elif chapter_id:
                code.chapter_id = chapter_id
            code.save()
            return redirect('literature:index')
    else:
        form = CodeForm()

    chapter_id = request.GET.get('chapter')
    section_id = request.GET.get('section')
    subsection_id = request.GET.get('subsection')
    subsubsection_id = request.GET.get('subsubsection')

    context = {
        'form': form,
        'title': 'Add Code',
        'chapter_id': chapter_id,
        'section_id': section_id,
        'subsection_id': subsection_id,
        'subsubsection_id': subsubsection_id,
    }
    return render(request, 'literature/code_form.html', context)

def update_code(request, pk):
    code = get_object_or_404(Code, pk=pk)
    if request.method == "POST":
        form = CodeForm(request.POST, instance=code)
        if form.is_valid():
            form.save()
            return redirect('literature:index')
    else:
        form = CodeForm(instance=code)
    return render(request, 'literature/form.html', {'form': form, 'title': 'Edit Code'})

def delete_code(request, pk):
    get_object_or_404(Code, pk=pk).delete()
    return redirect('literature:index')

def view_codes(request):
    chapter_id = request.GET.get('chapter')
    section_id = request.GET.get('section')
    subsection_id = request.GET.get('subsection')
    subsubsection_id = request.GET.get('subsubsection')

    codes = None
    parent_name = ""

    if subsubsection_id:
        parent = get_object_or_404(SubSubsection, pk=subsubsection_id)
        codes = parent.codes.all()
        parent_name = f"SubSubsection: {parent.subsubsection_name}"
    elif subsection_id:
        parent = get_object_or_404(Subsection, pk=subsection_id)
        codes = parent.codes.all()
        parent_name = f"Subsection: {parent.subsection_name}"
    elif section_id:
        parent = get_object_or_404(Section, pk=section_id)
        codes = parent.codes.all()
        parent_name = f"Section: {parent.section_name}"
    elif chapter_id:
        parent = get_object_or_404(Chapter, pk=chapter_id)
        codes = parent.codes.all()
        parent_name = f"Chapter: {parent.chapter_name}"

    return render(request, 'literature/view_codes.html', {
        'codes': codes,
        'parent_name': parent_name
    })


# ----- Notes -----

def add_note(request):
    """Add a new note to a chapter/section/subsection/subsubsection."""
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            # Attach to the right parent (from hidden POST fields)
            chapter_id = request.POST.get('chapter_id')
            section_id = request.POST.get('section_id')
            subsection_id = request.POST.get('subsection_id')
            subsubsection_id = request.POST.get('subsubsection_id')

            if subsubsection_id:
                note.subsubsection_id = subsubsection_id
            elif subsection_id:
                note.subsection_id = subsection_id
            elif section_id:
                note.section_id = section_id
            elif chapter_id:
                note.chapter_id = chapter_id

            # Save TipTap JSON content from hidden field
            content_json = request.POST.get('content_json', '{}')
            try:
                note.content = json.loads(content_json)
            except (json.JSONDecodeError, TypeError):
                note.content = {}

            note.save()
            return redirect('literature:index')
    else:
        form = NoteForm()

    # Which parent are we adding to?
    chapter_id = request.GET.get('chapter')
    section_id = request.GET.get('section')
    subsection_id = request.GET.get('subsection')
    subsubsection_id = request.GET.get('subsubsection')

    context = {
        'form': form,
        'title': 'Add Note',
        'note': None,  # new note, no existing content
        'chapter_id': chapter_id,
        'section_id': section_id,
        'subsection_id': subsection_id,
        'subsubsection_id': subsubsection_id,
        'content_json': '{}',
    }
    return render(request, 'literature/note_edit.html', context)


def edit_note(request, pk):
    """Edit an existing note."""
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            content_json = request.POST.get('content_json', '{}')
            try:
                note.content = json.loads(content_json)
            except (json.JSONDecodeError, TypeError):
                note.content = {}
            note.save()
            return redirect('literature:index')
    else:
        form = NoteForm(instance=note)

    import json as _json
    context = {
        'form': form,
        'title': f'Edit Note: {note.title or "Untitled"}',
        'note': note,
        'chapter_id': note.chapter_id,
        'section_id': note.section_id,
        'subsection_id': note.subsection_id,
        'subsubsection_id': note.subsubsection_id,
        'content_json': _json.dumps(note.content) if note.content else '{}',
    }
    return render(request, 'literature/note_edit.html', context)


def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect('literature:index')


@require_POST
def upload_note_image(request):
    """
    AJAX endpoint: receives an image file, saves it, returns the URL.
    TipTap calls this when the user inserts an image.
    """
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    image_file = request.FILES['image']
    note_image = NoteImage(image=image_file)
    note_image.save()

    return JsonResponse({'url': request.build_absolute_uri(note_image.image.url)})


@require_POST
def reorder_notes(request):
    """AJAX endpoint to save new note order via drag-and-drop."""
    try:
        data = json.loads(request.body)
        note_ids = data.get('note_ids', [])
        for index, note_id in enumerate(note_ids):
            Note.objects.filter(id=note_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ----- Reordering (existing, unchanged) -----

@require_POST
def reorder_chapters(request):
    try:
        data = json.loads(request.body)
        chapter_ids = data.get('chapter_ids', [])
        for index, chapter_id in enumerate(chapter_ids):
            Chapter.objects.filter(id=chapter_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def reorder_sections(request):
    try:
        data = json.loads(request.body)
        section_ids = data.get('section_ids', [])
        for index, section_id in enumerate(section_ids):
            Section.objects.filter(id=section_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def reorder_subsections(request):
    try:
        data = json.loads(request.body)
        subsection_ids = data.get('subsection_ids', [])
        for index, subsection_id in enumerate(subsection_ids):
            Subsection.objects.filter(id=subsection_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def reorder_subsubsections(request):
    try:
        data = json.loads(request.body)
        subsubsection_ids = data.get('subsubsection_ids', [])
        for index, subsubsection_id in enumerate(subsubsection_ids):
            SubSubsection.objects.filter(id=subsubsection_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def reorder_books(request):
    try:
        data = json.loads(request.body)
        book_ids = data.get('book_ids', [])
        for index, book_id in enumerate(book_ids):
            Book.objects.filter(id=book_id).update(order=index)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# 🎓 Academic Web
> An integrated Django workspace for scientific literature management, research synthesis, and structured technical writing.

**Academic Web** is a dual-purpose platform designed for researchers. It bridges the gap between **consuming** research (tracking papers, extracting specific claims) and **producing** research (writing books, documenting code, and organizing chapters).

---

# Academic Web

A Django-based web application for managing and showcasing academic papers and literature.

---

## Requirements

- Python 3.8+
- pip

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/biswanathmalaker/academic_web.git
cd academic_web
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Project Structure

The project consists of three Django apps:

| App | Purpose |
|---|---|
| `home` | Landing page and general site navigation |
| `papers` | Manage and display academic papers |
| `literature` | Manage and display literature references |

---

## Configuration

### URL Routing (`academic_web/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("home.urls")),
    path("papers/", include("papers.urls")),
    path("literature/", include("literature.urls")),
]

urlpatterns += static('/papers/pdf/', document_root=settings.BASE_DIR / 'papers/pdf')
```

### Installed Apps (`academic_web/settings.py`)

Ensure the following apps are listed under `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'papers',
    'home',
    'literature',
]
```

---

## Database Setup

After creating (or updating) the apps, run migrations:

```bash
python3 manage.py makemigrations papers literature home
python3 manage.py migrate
```

---

## Running the Development Server

```bash
python3 manage.py runserver 8080
```

The application will be available at **http://127.0.0.1:8080**

---

## Adding Papers

Papers can be added via the Django admin panel at **http://127.0.0.1:8080/admin**.

Each paper is automatically assigned a unique ID based on the author's name and year — for example:

```
malaker-2024
malaker-2024a
malaker-2024b
...
```

### Attaching PDF Files

To serve a paper's PDF, place the file inside the `papers/pdf/` directory, naming it after the paper's unique ID:

```
papers/
└── pdf/
    ├── malaker-2024.pdf
    ├── malaker-2024a.pdf
    └── ...
```

The PDFs will be served at `/papers/pdf/<paper-id>.pdf`.

---

## License

This project is open source. See the repository for license details.


---

## 🌟 Core Modules

### 1. 📚 Papers App (Research Intelligence)
The Papers module is designed to atomize scientific literature. Instead of just storing PDFs, it breaks papers down into "Statements" that can be cross-referenced.
* **Smart Citation Keys:** Automatically generates unique BibTeX keys (e.g., `weitz-2025a`) based on authorship and year.
* **Granular Statements:** Extract specific findings from the `Abstract`, `Methods`, or `Results` sections.
* **Topical Mapping:** Link statements to specific `Topics` (e.g., *magnetic fields*) and broader `Categories` (e.g., *Jets, Flares, Nebula*).
* **Citation Tracking:** A Many-to-Many relationship allows you to track exactly which papers cite specific statements in your database.

### 2. ✍️ Literature App (Structured Writing)
The Literature module provides a hierarchical framework for drafting your own books, thesis chapters, or technical manuals.
* **Deep Hierarchy:** Supports a 5-level structural depth: 
    `Book` → `Chapter` → `Section` → `Subsection` → `SubSubsection`.
* **Integrated Code snippets:** Attach `Code` objects directly to any level of the hierarchy. Perfect for keeping simulation code or data analysis scripts right next to the text that explains them.
* **Logical Ordering:** Every level includes an `order` field to ensure your Table of Contents remains consistent regardless of the order in which you input data.

---

## 🛠️ Technical Architecture

### Model Relationships
The system is built on a relational backbone that ensures data integrity:
- **Papers:** Uses `unique=True` on citation keys to prevent duplicate entries.
- **Literature:** Uses `ForeignKey` with `CASCADE` deletion, ensuring that if a Chapter is removed, all nested Sections and Subsections are cleaned up automatically.
- **Code:** Uses a flexible parent-lookup system (`get_parent()`) to identify which level of the hierarchy a snippet belongs to.

---

## 💾 Database Management & Migrations

Because this project uses custom logic for IDs and ContentTypes, it is critical to use the following commands when moving data between environments to avoid `IntegrityError`.

### Clean Data Export
Excludes internal Django management tables (auth, contenttypes) to ensure the fixture remains "pure" app data.
```bash
python3 manage.py dumpdata papers literature --indent 2 --exclude auth --exclude contenttypes > academic_data_clean.json
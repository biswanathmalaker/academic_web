# 🎓 Academic Web
> An integrated Django workspace for scientific literature management, research synthesis, and structured technical writing.

**Academic Web** is a dual-purpose platform designed for researchers. It bridges the gap between **consuming** research (tracking papers, extracting specific claims) and **producing** research (writing books, documenting code, and organizing chapters).

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
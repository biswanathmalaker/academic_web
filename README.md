# 🎓 academic Web
> A Django-powered research management tool designed to atomize academic papers into actionable insights, statements, and topical hierarchies.

Academic Web goes beyond simple bibliography management. It allows researchers to deconstruct papers into specific **Statements**, link them to **Topics**, and categorize the entire body of work into **Broad Categories** (e.g., *Flares, Jets, Star Formation*).

---

## 🚀 Key Features

* **Automated Citation Keys:** Intelligent generation of BibTeX-compatible keys (e.g., `weitz-2025a`) based on authorship and year.
* **Granular Statement Extraction:** Break papers down by section (Abstract, Methods, Results) to create a searchable knowledge base.
* **Relational Mapping:** Track which papers cite specific statements or findings directly.
* **Multi-Topic Tagging:** Use "Broad Topics" to filter your entire web view, allowing you to focus on one research domain at a time.

---

## 🛠️ Database Management

To maintain data integrity and avoid `IntegrityError` conflicts with Django's internal content types, use these specific commands for backups and migrations.

### Exporting Data (Backup)
To dump your research data while excluding internal system tables:
```bash
python3 manage.py dumpdata papers --indent 2 --exclude auth --exclude contenttypes > papers_clean.json
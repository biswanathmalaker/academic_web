// Initialize globals and configuration
window.__NOTE_CONTENT__ = window.__NOTE_CONTENT__ || {};
window.__UPLOAD_URL__ = window.__UPLOAD_URL__ || '';

// Get CSRF token from cookies
function getCookie(name) {
    let v = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) {
            v = decodeURIComponent(c.slice(name.length + 1));
        }
    });
    return v;
}

window.__CSRF__ = getCookie('csrftoken');

// Setup editor with TipTap (note: requires TipTap library to be loaded)
function initializeEditor() {
    // This function expects TipTap to be already loaded via CDN
    // Libraries needed: @tiptap/core, @tiptap/extension-*, katex
    
    if (typeof Editor === 'undefined') {
        console.error('TipTap Editor not found. Make sure TipTap is loaded.');
        return;
    }

    // Toolbar button functions
    function syncToolbar() {
        document.getElementById('btn-bold').classList.toggle('is-active', window.__editor.isActive('bold'));
        document.getElementById('btn-italic').classList.toggle('is-active', window.__editor.isActive('italic'));
        document.getElementById('btn-h1').classList.toggle('is-active', window.__editor.isActive('heading', {level: 1}));
        document.getElementById('btn-h2').classList.toggle('is-active', window.__editor.isActive('heading', {level: 2}));
        document.getElementById('btn-h3').classList.toggle('is-active', window.__editor.isActive('heading', {level: 3}));
        document.getElementById('btn-bullet').classList.toggle('is-active', window.__editor.isActive('bulletList'));
        document.getElementById('btn-ordered').classList.toggle('is-active', window.__editor.isActive('orderedList'));
    }

    // Toolbar button listeners
    document.getElementById('btn-bold').addEventListener('click', () => {
        window.__editor.chain().focus().toggleBold().run();
        syncToolbar();
    });
    document.getElementById('btn-italic').addEventListener('click', () => {
        window.__editor.chain().focus().toggleItalic().run();
        syncToolbar();
    });
    document.getElementById('btn-h1').addEventListener('click', () => {
        window.__editor.chain().focus().toggleHeading({level: 1}).run();
        syncToolbar();
    });
    document.getElementById('btn-h2').addEventListener('click', () => {
        window.__editor.chain().focus().toggleHeading({level: 2}).run();
        syncToolbar();
    });
    document.getElementById('btn-h3').addEventListener('click', () => {
        window.__editor.chain().focus().toggleHeading({level: 3}).run();
        syncToolbar();
    });
    document.getElementById('btn-bullet').addEventListener('click', () => {
        window.__editor.chain().focus().toggleBulletList().run();
        syncToolbar();
    });
    document.getElementById('btn-ordered').addEventListener('click', () => {
        window.__editor.chain().focus().toggleOrderedList().run();
        syncToolbar();
    });
    document.getElementById('btn-undo').addEventListener('click', () => {
        window.__editor.chain().focus().undo().run();
        syncToolbar();
    });
    document.getElementById('btn-redo').addEventListener('click', () => {
        window.__editor.chain().focus().redo().run();
        syncToolbar();
    });

    // Image upload handler
    document.getElementById('btn-image').addEventListener('click', () => {
        document.getElementById('image-file-input').click();
    });

    document.getElementById('image-file-input').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const fd = new FormData();
        fd.append('image', file);
        try {
            const res = await fetch(window.__UPLOAD_URL__, {
                method: 'POST',
                headers: {'X-CSRFToken': window.__CSRF__},
                body: fd
            });
            const data = await res.json();
            if (data.url) {
                window.__editor.chain().focus().insertContent({
                    type: 'resizableImage',
                    attrs: { src: data.url, alt: file.name, width: 400 }
                }).run();
            } else {
                alert('Upload failed: ' + (data.error || 'unknown'));
            }
        } catch (err) {
            alert('Upload error: ' + err);
        }
        e.target.value = '';
    });

    // LaTeX modal setup
    let _latexCallback = null;

    function openLatexModal(existing = '', existingDisplay = false, cb = null) {
        _latexCallback = cb;
        document.getElementById('latex-input').value = existing;
        document.getElementById('latex-block-mode').checked = existingDisplay;
        previewLatex();
        document.getElementById('latex-modal').classList.add('open');
        setTimeout(() => document.getElementById('latex-input').focus(), 60);
    }

    function previewLatex() {
        const latex = document.getElementById('latex-input').value.trim();
        const display = document.getElementById('latex-block-mode').checked;
        const el = document.getElementById('latex-preview');
        if (!latex) {
            el.textContent = 'Preview appears here…';
            return;
        }
        try {
            if (window.katex) {
                katex.render(latex, el, { throwOnError: false, displayMode: display });
            } else {
                el.textContent = latex;
            }
        } catch (e) {
            el.textContent = 'Invalid LaTeX';
        }
    }

    document.getElementById('latex-input').addEventListener('input', previewLatex);
    document.getElementById('latex-block-mode').addEventListener('change', previewLatex);
    document.getElementById('btn-latex').addEventListener('click', () => openLatexModal('', false, null));

    document.getElementById('latex-confirm').addEventListener('click', () => {
        const latex = document.getElementById('latex-input').value.trim();
        const display = document.getElementById('latex-block-mode').checked;
        if (!latex) return;
        if (_latexCallback) {
            _latexCallback(latex, display);
        } else {
            window.__editor.chain().focus().insertContent({
                type: 'latex',
                attrs: {latex, display}
            }).run();
        }
        document.getElementById('latex-modal').classList.remove('open');
        _latexCallback = null;
    });

    document.getElementById('latex-cancel').addEventListener('click', () => {
        document.getElementById('latex-modal').classList.remove('open');
        _latexCallback = null;
    });

    document.getElementById('latex-modal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('latex-modal')) {
            document.getElementById('latex-modal').classList.remove('open');
            _latexCallback = null;
        }
    });

    // Form submission handler
    document.getElementById('note-form').addEventListener('submit', () => {
        if (window.__editor) {
            document.getElementById('content_json').value = JSON.stringify(window.__editor.getJSON());
        }
    });

    // Update editor reference when it's created
    window.__editorInitialized = true;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEditor);
} else {
    initializeEditor();
}

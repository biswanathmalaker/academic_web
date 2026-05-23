// Setup globals and CSRF token
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
window.__NOTE_CONTENT__ = window.__NOTE_CONTENT__ || {};
window.__UPLOAD_URL__ = window.__UPLOAD_URL__ || '';

// Toolbar sync function
window.syncToolbar = function() {
    if (!window.__editor) return;
    document.getElementById('btn-bold').classList.toggle('is-active', window.__editor.isActive('bold'));
    document.getElementById('btn-italic').classList.toggle('is-active', window.__editor.isActive('italic'));
    document.getElementById('btn-h1').classList.toggle('is-active', window.__editor.isActive('heading', {level: 1}));
    document.getElementById('btn-h2').classList.toggle('is-active', window.__editor.isActive('heading', {level: 2}));
    document.getElementById('btn-h3').classList.toggle('is-active', window.__editor.isActive('heading', {level: 3}));
    document.getElementById('btn-bullet').classList.toggle('is-active', window.__editor.isActive('bulletList'));
    document.getElementById('btn-ordered').classList.toggle('is-active', window.__editor.isActive('orderedList'));
};

// Setup toolbar handlers
window.setupToolbarHandlers = function(editor) {
    window.__editor = editor;

    // Toolbar button listeners
    document.getElementById('btn-bold').addEventListener('click', () => {
        editor.chain().focus().toggleBold().run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-italic').addEventListener('click', () => {
        editor.chain().focus().toggleItalic().run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-h1').addEventListener('click', () => {
        editor.chain().focus().toggleHeading({level: 1}).run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-h2').addEventListener('click', () => {
        editor.chain().focus().toggleHeading({level: 2}).run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-h3').addEventListener('click', () => {
        editor.chain().focus().toggleHeading({level: 3}).run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-bullet').addEventListener('click', () => {
        editor.chain().focus().toggleBulletList().run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-ordered').addEventListener('click', () => {
        editor.chain().focus().toggleOrderedList().run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-undo').addEventListener('click', () => {
        editor.chain().focus().undo().run();
        window.syncToolbar();
    });
    
    document.getElementById('btn-redo').addEventListener('click', () => {
        editor.chain().focus().redo().run();
        window.syncToolbar();
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
                editor.chain().focus().insertContent({
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

    window.openLatexModal = function(existing = '', existingDisplay = false, cb = null) {
        _latexCallback = cb;
        document.getElementById('latex-input').value = existing;
        document.getElementById('latex-block-mode').checked = existingDisplay;
        window.previewLatex();
        document.getElementById('latex-modal').classList.add('open');
        setTimeout(() => document.getElementById('latex-input').focus(), 60);
    };

    window.previewLatex = function() {
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
    };

    document.getElementById('latex-input').addEventListener('input', window.previewLatex);
    document.getElementById('latex-block-mode').addEventListener('change', window.previewLatex);
    document.getElementById('btn-latex').addEventListener('click', () => window.openLatexModal('', false, null));

    document.getElementById('latex-confirm').addEventListener('click', () => {
        const latex = document.getElementById('latex-input').value.trim();
        const display = document.getElementById('latex-block-mode').checked;
        if (!latex) return;
        if (_latexCallback) {
            _latexCallback(latex, display);
        } else {
            editor.chain().focus().insertContent({
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
        if (editor) {
            document.getElementById('content_json').value = JSON.stringify(editor.getJSON());
        }
    });
};

// Initialize when DOM is ready if editor is already available
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.__editor && !window._handlersSetup) {
            window.setupToolbarHandlers(window.__editor);
            window._handlersSetup = true;
        }
    });
} else {
    if (window.__editor && !window._handlersSetup) {
        window.setupToolbarHandlers(window.__editor);
        window._handlersSetup = true;
    }
}


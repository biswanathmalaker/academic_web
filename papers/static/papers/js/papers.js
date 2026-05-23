/* ── Copy BibTeX ─────────────────────────────────────────────────────────── */
function copyBibtex(paperKey, rawBibtex) {
    if (!rawBibtex) return;
    const modified = rawBibtex.replace(/@(\w+)\s*\{[^,]*,/, (_, type) => `@${type}{${paperKey},`);
    navigator.clipboard.writeText(modified);
}

/* ── Offcanvas tab switcher ──────────────────────────────────────────────── */
function switchTab(btn, targetId) {
    // find all panes and tabs within same offcanvas
    const offcanvas = btn.closest('.offcanvas-body');
    offcanvas.querySelectorAll('.tab-pane-content').forEach(p => p.style.display = 'none');
    offcanvas.querySelectorAll('.nav-link').forEach(b => b.classList.remove('active'));
    document.getElementById(targetId).style.display = 'block';
    btn.classList.add('active');
}

/* ── Open offcanvas on correct tab when clicking stat chips ─────────────── */
document.querySelectorAll('[data-tab]').forEach(el => {
    el.addEventListener('click', function () {
        const target = this.getAttribute('data-bs-target');   // e.g. #sidebar42
        const tab    = this.getAttribute('data-tab');         // refs or cites
        const paperId = target.replace('#sidebar', '');
        // Switch tab after offcanvas opens
        setTimeout(() => {
            const paneId = tab + paperId;
            const offcanvas = document.querySelector(target + ' .offcanvas-body');
            if (!offcanvas) return;
            offcanvas.querySelectorAll('.tab-pane-content').forEach(p => p.style.display = 'none');
            offcanvas.querySelectorAll('.nav-link').forEach(b => b.classList.remove('active'));
            const pane = document.getElementById(paneId);
            if (pane) pane.style.display = 'block';
            const activeBtn = offcanvas.querySelector(`[data-tab-target="${paneId}"]`);
            if (activeBtn) activeBtn.classList.add('active');
        }, 150);
    });
});

/* ── Make Core (AJAX) ────────────────────────────────────────────────────── */
document.querySelectorAll('.make-core-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
        const paperId = this.dataset.paperId;
        const itemId  = this.dataset.itemId;
        const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';

        try {
            const resp = await fetch(`/papers/paper/${paperId}/make-core/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
            });
            if (resp.ok) {
                const item = document.getElementById(itemId);
                if (item) {
                    item.classList.add('is-core');
                    // Replace button with CORE badge
                    this.outerHTML = `<span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-25" style="font-size:0.65rem;">CORE</span>`;
                }
            }
        } catch (e) {
            console.error('Make core failed:', e);
        }
    });
});

/* ── ADS update button spinner ───────────────────────────────────────────── */
document.querySelectorAll('.ads-update-form').forEach(form => {
    form.addEventListener('submit', function () {
        const btn = this.querySelector('.ads-update-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spin"><i class="bi bi-arrow-clockwise"></i></span> Updating…';
    });
});

/* ── Auto-dismiss session flash after 6s ────────────────────────────────── */
setTimeout(() => {
    document.querySelectorAll('.alert-dismissible').forEach(a => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
        bsAlert.close();
    });
}, 6000);

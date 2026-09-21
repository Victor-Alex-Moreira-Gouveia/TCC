const BASE = '/api/ajuda';

function log(msg) {
    document.getElementById('log').textContent =
        (typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2));
}

async function apiFetch(url, opts = {}) {
    const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
    if (r.status === 204) return { success: true, message: 'Registro deletado com sucesso (204)' };
    return r.json();
}

async function createAjuda() {
    const body = {
        titulo: document.getElementById('c-titulo').value,
        corpo: document.getElementById('c-corpo').value,
    };
    const res = await apiFetch(BASE, { method: 'POST', body: JSON.stringify(body) });
    log(res);
    if (res.success) {
        loadAjuda();
        document.getElementById('c-titulo').value = '';
        document.getElementById('c-corpo').value = '';
    }
}

async function loadAjuda() {
    const res = await apiFetch(BASE);
    log(res);
    const tbody = document.querySelector('#tbl-ajuda tbody');
    tbody.innerHTML = '';

    if (!res.data || res.data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">Nenhum registro encontrado.</td></tr>`;
        return;
    }

    res.data.forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td class="fw-bold text-secondary">${escHtml(String(a.id))}</td>
        <td class="fw-semibold">${escHtml(a.titulo)}</td>
        <td class="corpo-cell-truncated text-muted" title="${escHtml(a.corpo)}">${escHtml(a.corpo)}</td>
        <td>
            <div class="d-flex gap-2 justify-content-center">
            <button class="btn btn-sm btn-outline-primary" title="Editar" onclick="fillUpdate(${a.id},'${esc(a.titulo)}','${esc(a.corpo)}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" title="Excluir" onclick="deleteAjuda(${a.id})">
                <i class="bi bi-trash"></i>
            </button>
            </div>
        </td>`;
        tbody.appendChild(tr);
    });
}

function esc(s) { return (s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n'); }

function escHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function (m) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[m];
    });
}

function fillUpdate(id, titulo, corpo) {
    document.getElementById('u-id').value = id;
    document.getElementById('u-titulo').value = titulo;
    document.getElementById('u-corpo').value = corpo;
    document.getElementById('u-id').scrollIntoView({ behavior: 'smooth' });
}

async function updateAjuda() {
    const id = document.getElementById('u-id').value;
    if (!id) { log('Erro: Informe o ID do registro para atualizar.'); return; }
    const body = {};
    const t = document.getElementById('u-titulo').value.trim();
    const c = document.getElementById('u-corpo').value.trim();
    if (t) body.titulo = t;
    if (c) body.corpo = c;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(body) });
    log(res);
    if (res.success) loadAjuda();
}

async function deleteAjuda(id) {
    if (!confirm(`Tem certeza que deseja excluir permanentemente o registro ID ${id}?`)) return;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'DELETE' });
    log(res);
    loadAjuda();
}

function clearLog() { document.getElementById('log').textContent = '— terminal limpo —'; }

loadAjuda();
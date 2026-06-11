const BASE = '/api/noticias';

function log(msg) {
    document.getElementById('log').textContent =
        (typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2));
}

async function apiFetch(url, opts = {}) {
    const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
    if (r.status === 204) return { success: true, message: 'Notícia excluída com sucesso (204)' };
    return r.json();
}

async function createNoticia() {
    const body = {
        titulo: document.getElementById('c-titulo').value,
        corpo:  document.getElementById('c-corpo').value,
    };
    const res = await apiFetch(BASE, { method: 'POST', body: JSON.stringify(body) });
    log(res);
    if (res.success) {
        loadNoticias();
        // Limpa o formulário após criar
        document.getElementById('c-titulo').value = '';
        document.getElementById('c-corpo').value = '';
    }
}

async function loadNoticias() {
    const res = await apiFetch(BASE);
    log(res);
    const tbody = document.querySelector('#tbl-noticias tbody');
    tbody.innerHTML = '';

    if (!res.data || res.data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">Nenhuma notícia localizada.</td></tr>`;
        return;
    }

    res.data.forEach(n => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td class="fw-bold text-secondary">${n.id}</td>
        <td class="fw-semibold text-dark">${n.titulo}</td>
        <td class="corpo-cell-truncated text-muted small" title="${n.corpo}">${n.corpo}</td>
        <td class="text-secondary small font-monospace">${n.data_hora || '—'}</td>
        <td>
            <div class="d-flex gap-2 justify-content-center">
            <button class="btn btn-sm btn-outline-primary" title="Editar" onclick="fillUpdate(${n.id},'${escJs(n.titulo)}','${escJs(n.corpo)}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" title="Excluir" onclick="deleteNoticia(${n.id})">
                <i class="bi bi-trash"></i>
            </button>
            </div>
        </td>`;
        tbody.appendChild(tr);
    });
}

function escJs(s) { return (s||'').replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/\n/g,'\\n'); }

function fillUpdate(id, titulo, corpo) {
    document.getElementById('u-id').value = id;
    document.getElementById('u-titulo').value = titulo;
    document.getElementById('u-corpo').value = corpo;

    // Foca e rola suavemente até o formulário de edição
    document.getElementById('u-id').scrollIntoView({ behavior: 'smooth' });
}

async function updateNoticia() {
    const id = document.getElementById('u-id').value;
    if (!id) { log('Erro: Informe o ID da notícia para atualizar.'); return; }
    const body = {};
    const t = document.getElementById('u-titulo').value.trim();
    const c = document.getElementById('u-corpo').value.trim();
    if (t) body.titulo = t;
    if (c) body.corpo  = c;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(body) });
    log(res);
    if (res.success) loadNoticias();
}

async function deleteNoticia(id) {
    if (!confirm(`Tem certeza que deseja remover permanentemente o artigo de ID ${id}?`)) return;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'DELETE' });
    log(res);
    loadNoticias();
}

function clearLog() { document.getElementById('log').textContent = '— terminal limpo —'; }

// Inicializa os dados na tabela automaticamente
loadNoticias();
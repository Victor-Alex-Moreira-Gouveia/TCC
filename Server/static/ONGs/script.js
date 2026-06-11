const BASE = '/api/ongs';

function log(msg) {
    document.getElementById('log').textContent =
        (typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2));
}

async function apiFetch(url, opts = {}) {
    const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
    if (r.status === 204) return { success: true, message: 'ONG deletada com sucesso (204)' };
    return r.json();
}

async function createOng() {
    const body = {
        nome_instituicao: document.getElementById('c-nome').value,
        endereco_fisico:  document.getElementById('c-end').value  || null,
        site:             document.getElementById('c-site').value || null,
        pix_doacao:       document.getElementById('c-pix').value,
    };
    const res = await apiFetch(BASE, { method: 'POST', body: JSON.stringify(body) });
    log(res);
    if (res.success) {
        loadOngs();
        // Limpa formulário após criação
        document.getElementById('c-nome').value = '';
        document.getElementById('c-end').value = '';
        document.getElementById('c-site').value = '';
        document.getElementById('c-pix').value = '';
    }
}

async function loadOngs() {
    const res = await apiFetch(BASE);
    log(res);
    const tbody = document.querySelector('#tbl-ongs tbody');
    tbody.innerHTML = '';

    if(!res.data || res.data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">Nenhuma ONG cadastrada no momento.</td></tr>`;
        return;
    }

    res.data.forEach(o => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td class="fw-bold text-secondary">${o.id}</td>
        <td class="fw-semibold text-dark">${o.nome_instituicao}</td>
        <td class="text-muted small">${o.endereco_fisico || '—'}</td>
        <td>${o.site ? `<a href="${o.site}" target="_blank" class="text-brand text-decoration-none fw-semibold small"><i class="bi bi-box-arrow-up-right me-1"></i>Visitar</a>` : '<span class="text-muted">—</span>'}</td>
        <td><span class="badge bg-light text-dark font-monospace border">${o.pix_doacao}</span></td>
        <td>
            <div class="d-flex gap-2 justify-content-center">
            <button class="btn btn-sm btn-outline-primary" title="Editar" onclick="fillUpdate(${o.id},'${e(o.nome_instituicao)}','${e(o.endereco_fisico)}','${e(o.site)}','${e(o.pix_doacao)}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" title="Excluir" onclick="deleteOng(${o.id})">
                <i class="bi bi-trash"></i>
            </button>
            </div>
        </td>`;
        tbody.appendChild(tr);
    });
}

function e(s) { return (s || '').replace(/\\/g,'\\\\').replace(/'/g,"\\'"); }

function fillUpdate(id, nome, end, site, pix) {
    document.getElementById('u-id').value   = id;
    document.getElementById('u-nome').value = nome;
    document.getElementById('u-end').value  = end === 'null' ? '' : end;
    document.getElementById('u-site').value = site === 'null' ? '' : site;
    document.getElementById('u-pix').value  = pix;

    // Scroll focado para o formulário de atualização
    document.getElementById('u-id').scrollIntoView({ behavior: 'smooth' });
}

async function updateOng() {
    const id = document.getElementById('u-id').value;
    if (!id) { log('Erro: Informe o ID da ONG para realizar a alteração.'); return; }
    const body = {};
    const nome = document.getElementById('u-nome').value.trim();
    const end  = document.getElementById('u-end').value.trim();
    const site = document.getElementById('u-site').value.trim();
    const pix  = document.getElementById('u-pix').value.trim();
    if (nome) body.nome_instituicao = nome;
    if (end !== '') body.endereco_fisico = end || null;
    if (site !== '') body.site = site || null;
    if (pix) body.pix_doacao = pix;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(body) });
    log(res);
    if (res.success) loadOngs();
}

async function deleteOng(id) {
    if (!confirm(`Tem certeza que deseja remover permanentemente a ONG de ID ${id}?`)) return;
    const res = await apiFetch(`${BASE}/${id}`, { method: 'DELETE' });
    log(res);
    loadOngs();
}

function clearLog() { document.getElementById('log').textContent = '— terminal limpo —'; }

// Sincroniza os dados automaticamente ao abrir a página
loadOngs();
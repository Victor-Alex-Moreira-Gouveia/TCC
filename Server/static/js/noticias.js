document.addEventListener('DOMContentLoaded', () => {
    carregarNoticias();
});

let modalNoticiaBS = null;
let modalConfirmarBS = null;
let acaoConfirmarCallback = null;

// Exibe mensagem de notificação com estado visual reutilizável
function exibirAlerta(mensagem, tipo = 'success') {
    const container = document.getElementById('alert-global');
    if (!container) return;

    container.className = `alert alert-${tipo} alert-dismissible fade show shadow-sm`;
    container.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${tipo === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill'} me-2 fs-5"></i>
            <div>${mensagem}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        </div>
    `;
    container.classList.remove('d-none');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    setTimeout(() => {
        if (container && !container.classList.contains('d-none')) {
            container.classList.add('d-none');
        }
    }, 5000);
}

// Carrega e renderiza a lista de notícias da API
async function carregarNoticias() {
    const container = document.getElementById('noticias-list');
    if (!container) return;

    try {
        const response = await fetch('/api/noticias');
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            if (!resultado.data || resultado.data.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-5 text-white">
                        <i class="bi bi-newspaper fs-1"></i>
                        <p class="mt-2 mb-0 fs-5">Nenhuma notícia cadastrada no momento.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = '';
            resultado.data.forEach(noticia => {
                const card = criarCardNoticiaHTML(noticia);
                container.insertAdjacentHTML('beforeend', card);
            });
        } else {
            container.innerHTML = `
                <div class="alert alert-danger text-center" role="alert">
                    ${resultado.error || 'Erro ao carregar lista de notícias.'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro de conexão ao carregar notícias:', error);
        container.innerHTML = `
            <div class="alert alert-danger text-center" role="alert">
                Erro de conexão com o servidor de notícias.
            </div>
        `;
    }
}

// Constrói o HTML do card de cada notícia
function criarCardNoticiaHTML(noticia) {
    const dataFormatada = noticia.data_hora 
        ? new Date(noticia.data_hora).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        : 'Data não informada';

    const corpoFormatado = noticia.corpo ? escapeHTML(noticia.corpo).replace(/\n/g, '<br>') : '';
    const isAdmin = window.CURRENT_USER_ROLE === 'admin';
    const curtido = noticia.curtido_pelo_usuario ? 'ativo' : '';
    const imageTag = noticia.imagem_url 
        ? `<img src="${escapeHTML(noticia.imagem_url)}" alt="${escapeHTML(noticia.titulo)}" class="noticia-img">` 
        : '';

    const adminButtons = isAdmin ? `
        <div class="dropdown ms-auto">
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle rounded-pill" type="button" data-bs-toggle="dropdown">
                <i class="bi bi-gear-fill"></i> Gerenciar
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                <li><a class="dropdown-item text-primary" href="#" onclick="abrirModalEditarNoticia(${noticia.id}); return false;"><i class="bi bi-pencil me-2"></i>Editar Notícia</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-danger" href="#" onclick="confirmarExclusaoNoticia(${noticia.id}); return false;"><i class="bi bi-trash me-2"></i>Excluir Notícia</a></li>
            </ul>
        </div>
    ` : '';

    return `
        <article class="noticia" id="noticia-card-${noticia.id}">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="data mb-0">
                    <i class="bi bi-calendar3"></i> ${dataFormatada}
                </div>
                ${adminButtons}
            </div>

            <h2 class="h4 font-weight-bold my-2" style="color: #7a4b00;">${escapeHTML(noticia.titulo)}</h2>
            ${imageTag}
            <div class="card-text text-secondary mb-3" style="line-height: 1.7;">
                ${corpoFormatado}
            </div>

            <div class="acoes">
                <button class="btn-reacao ${curtido}" id="btn-like-${noticia.id}" onclick="toggleCurtida(${noticia.id}, ${noticia.curtido_pelo_usuario})">
                    🐾 <i class="bi bi-heart-fill"></i> Curtir <span id="curtidas-count-${noticia.id}">${noticia.curtidas_count || 0}</span>
                </button>
                <button class="btn-comentario" onclick="alternarComentarios(${noticia.id})">
                    <i class="bi bi-chat-fill"></i> Comentar <span id="comentarios-count-${noticia.id}">${noticia.comentarios_count || 0}</span>
                </button>
                <button class="btn-compartilhar" onclick="compartilharNoticia(this)">
                    <i class="bi bi-share-fill"></i> Compartilhar
                </button>
            </div>

            <div class="menu-compartilhar" id="menuCompartilhar-${noticia.id}">
                <a href="#" class="btn-whatsapp" onclick="compartilharWhatsApp(event, this)">
                    <i class="bi bi-whatsapp"></i> WhatsApp
                </a>
                <a href="#" class="btn-facebook" onclick="compartilharFacebook(event, this)">
                    <i class="bi bi-facebook"></i> Facebook
                </a>
                <a href="#" class="btn-x" onclick="compartilharX(event, this)">
                    <i class="bi bi-twitter-x"></i> X
                </a>
                <button class="btn-copiar" onclick="copiarLinkNoticia(this)">
                    <i class="bi bi-link-45deg"></i> Copiar link
                </button>
            </div>

            <div class="comentarios" id="comentarios-${noticia.id}">
                <h5 class="h6 fw-bold text-brand mb-3"><i class="bi bi-chat-dots-fill me-1"></i> Comentários 🐾</h5>
                <div id="lista-comentarios-${noticia.id}" class="mb-3">
                    <small class="text-muted">Clique para carregar comentários...</small>
                </div>
                <div class="form-comentario">
                    <input type="text" id="input-comentario-${noticia.id}" placeholder="Escreva seu comentário respeitoso..." maxlength="1000">
                    <button class="btn-enviar" onclick="enviarComentario(${noticia.id})">Enviar 🐾</button>
                </div>
            </div>
        </article>
    `;
}

// Admin: Criar nova notícia
function abrirModalCriarNoticia() {
    document.getElementById('noticia-id').value = '';
    document.getElementById('noticia-titulo').value = '';
    document.getElementById('noticia-corpo').value = '';
    const imgInput = document.getElementById('noticia-imagem');
    if (imgInput) imgInput.value = '';
    document.getElementById('modalNoticiaLabel').textContent = 'Cadastrar Nova Notícia';
    document.getElementById('btnSalvarNoticia').textContent = 'Cadastrar Notícia';

    if (!modalNoticiaBS) {
        modalNoticiaBS = new bootstrap.Modal(document.getElementById('modalNoticia'));
    }
    modalNoticiaBS.show();
}

// Admin: Editar notícia existente
async function abrirModalEditarNoticia(id) {
    try {
        const response = await fetch(`/api/noticias/${id}`);
        const data = await response.json();

        if (response.ok && data.success) {
            document.getElementById('noticia-id').value = data.data.id;
            document.getElementById('noticia-titulo').value = data.data.titulo;
            document.getElementById('noticia-corpo').value = data.data.corpo;
            const imgInput = document.getElementById('noticia-imagem');
            if (imgInput) imgInput.value = data.data.imagem_url || '';
            document.getElementById('modalNoticiaLabel').textContent = 'Editar Notícia';
            document.getElementById('btnSalvarNoticia').textContent = 'Atualizar Notícia';

            if (!modalNoticiaBS) {
                modalNoticiaBS = new bootstrap.Modal(document.getElementById('modalNoticia'));
            }
            modalNoticiaBS.show();
        } else {
            exibirAlerta(data.error || 'Erro ao buscar detalhes da notícia.', 'danger');
        }
    } catch (e) {
        exibirAlerta('Erro de conexão ao buscar notícia.', 'danger');
    }
}

// Admin: Salva (Criar ou Atualizar) notícia via API
async function salvarNoticia() {
    const id = document.getElementById('noticia-id').value;
    const titulo = document.getElementById('noticia-titulo').value.trim();
    const corpo = document.getElementById('noticia-corpo').value.trim();
    const imgInput = document.getElementById('noticia-imagem');
    const imagem_url = imgInput ? imgInput.value.trim() : '';

    if (!titulo || !corpo) {
        alert('Preencha título e corpo da notícia.');
        return;
    }

    const isEdit = Boolean(id);
    const url = isEdit ? `/api/noticias/${id}` : '/api/noticias';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, corpo, imagem_url })
        });
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            if (modalNoticiaBS) modalNoticiaBS.hide();
            exibirAlerta(resultado.message || (isEdit ? 'Notícia atualizada com sucesso.' : 'Notícia cadastrada com sucesso.'), 'success');
            carregarNoticias();
        } else {
            alert(resultado.error || 'Erro ao salvar notícia.');
        }
    } catch (e) {
        alert('Erro de conexão com o servidor.');
    }
}

// Admin: Confirmar remoção de notícia
function confirmarExclusaoNoticia(id) {
    document.getElementById('modalConfirmarTitulo').textContent = 'Confirmar Exclusão de Notícia';
    document.getElementById('modalConfirmarMensagem').textContent = `Deseja realmente excluir permanentemente a notícia ID ${id}?`;

    acaoConfirmarCallback = async () => {
        try {
            const response = await fetch(`/api/noticias/${id}`, { method: 'DELETE' });
            if (response.ok) {
                if (modalConfirmarBS) modalConfirmarBS.hide();
                exibirAlerta('Notícia removida com sucesso.', 'success');
                carregarNoticias();
            } else {
                const data = await response.json();
                exibirAlerta(data.error || 'Falha ao remover notícia.', 'danger');
            }
        } catch (e) {
            exibirAlerta('Erro de conexão ao remover notícia.', 'danger');
        }
    };

    document.getElementById('btnConfirmarAcao').onclick = acaoConfirmarCallback;

    if (!modalConfirmarBS) {
        modalConfirmarBS = new bootstrap.Modal(document.getElementById('modalConfirmar'));
    }
    modalConfirmarBS.show();
}

// Reação de Curtida em Notícia
async function toggleCurtida(noticiaId, estaCurtidoAtual) {
    const btn = document.getElementById(`btn-like-${noticiaId}`);
    const isCurrentlyActive = btn ? btn.classList.contains('ativo') : Boolean(estaCurtidoAtual);
    const method = isCurrentlyActive ? 'DELETE' : 'POST';

    try {
        const response = await fetch(`/api/noticias/${noticiaId}/curtida`, { method: method });
        const data = await response.json();

        if (response.ok && data.success) {
            const countSpan = document.getElementById(`curtidas-count-${noticiaId}`);
            if (countSpan) countSpan.textContent = data.data.curtidas_count;

            if (data.data.curtido_pelo_usuario) {
                btn.classList.add('ativo');
                btn.setAttribute('onclick', `toggleCurtida(${noticiaId}, true)`);
            } else {
                btn.classList.remove('ativo');
                btn.setAttribute('onclick', `toggleCurtida(${noticiaId}, false)`);
            }
        } else {
            exibirAlerta(data.error || 'Erro ao processar curtida.', 'warning');
        }
    } catch (e) {
        console.error('Erro de conexão na curtida:', e);
    }
}

// Alterna exibição e carrega lista de comentários da notícia
async function alternarComentarios(noticiaId) {
    const box = document.getElementById(`comentarios-${noticiaId}`);
    if (!box) return;

    box.classList.toggle('aberto');
    if (box.classList.contains('aberto')) {
        carregarComentarios(noticiaId);
    }
}

// Carrega os comentários da notícia via API
async function carregarComentarios(noticiaId) {
    const listDiv = document.getElementById(`lista-comentarios-${noticiaId}`);
    if (!listDiv) return;

    try {
        const response = await fetch(`/api/noticias/${noticiaId}/comentarios`);
        const data = await response.json();

        if (response.ok && data.success) {
            const comments = data.data || [];
            const countSpan = document.getElementById(`comentarios-count-${noticiaId}`);
            if (countSpan) countSpan.textContent = comments.length;

            if (comments.length === 0) {
                listDiv.innerHTML = '<p class="text-muted small my-2">Nenhum comentário ainda. Seja o primeiro a comentar!</p>';
                return;
            }

            listDiv.innerHTML = '';
            comments.forEach(c => {
                const isOwner = String(c.usuario_id) === String(window.CURRENT_USER_ID);
                const isAdmin = window.CURRENT_USER_ROLE === 'admin';
                const canManage = isOwner || isAdmin;

                const dataComentario = c.data_criacao 
                    ? new Date(c.data_criacao).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
                    : '';

                const acoesComentario = canManage ? `
                    <div class="comentario-acoes ms-auto">
                        <button class="btn btn-link text-secondary btn-sm-icon" title="Editar" onclick="editarComentario(${c.id}, '${escapeJS(c.texto)}', ${noticiaId})">
                            <i class="bi bi-pencil-fill"></i>
                        </button>
                        <button class="btn btn-link text-danger btn-sm-icon" title="Excluir" onclick="deletarComentario(${c.id}, ${noticiaId})">
                            <i class="bi bi-trash-fill"></i>
                        </button>
                    </div>
                ` : '';

                const cHtml = `
                    <div class="comentario shadow-sm p-3 mb-2 rounded-3" id="comentario-item-${c.id}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong class="text-brand me-2"><i class="bi bi-person-circle"></i> ${escapeHTML(c.autor_nome)}</strong>
                            <small class="text-muted me-2" style="font-size: 0.75rem;">${dataComentario}</small>
                            ${acoesComentario}
                        </div>
                        <div class="text-dark small text-break mb-0" id="comentario-texto-${c.id}">${escapeHTML(c.texto)}</div>
                    </div>
                `;
                listDiv.insertAdjacentHTML('beforeend', cHtml);
            });
        }
    } catch (e) {
        listDiv.innerHTML = '<p class="text-danger small">Erro ao carregar comentários.</p>';
    }
}

// Envia novo comentário
async function enviarComentario(noticiaId) {
    const input = document.getElementById(`input-comentario-${noticiaId}`);
    if (!input) return;

    const texto = input.value.trim();
    if (!texto) return;

    try {
        const response = await fetch(`/api/noticias/${noticiaId}/comentarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto })
        });
        const data = await response.json();

        if (response.ok && data.success) {
            input.value = '';
            exibirAlerta('Comentário adicionado com sucesso.', 'success');
            carregarComentarios(noticiaId);
        } else {
            exibirAlerta(data.error || 'Erro ao publicar comentário.', 'danger');
        }
    } catch (e) {
        exibirAlerta('Erro de conexão ao enviar comentário.', 'danger');
    }
}

// Edita comentário do próprio usuário ou admin
async function editarComentario(comentarioId, textoAtual, noticiaId) {
    const novoTexto = prompt('Editar comentário:', textoAtual);
    if (novoTexto === null) return;
    const textoLimpo = novoTexto.trim();

    if (!textoLimpo) {
        alert('O comentário não pode ser vazio.');
        return;
    }

    try {
        const response = await fetch(`/api/comentarios/${comentarioId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: textoLimpo })
        });
        const data = await response.json();

        if (response.ok && data.success) {
            exibirAlerta('Comentário atualizado com sucesso.', 'success');
            carregarComentarios(noticiaId);
        } else {
            exibirAlerta(data.error || 'Erro ao atualizar comentário.', 'danger');
        }
    } catch (e) {
        exibirAlerta('Erro de conexão ao editar comentário.', 'danger');
    }
}

// Deleta comentário
async function deletarComentario(comentarioId, noticiaId) {
    if (!confirm('Deseja realmente remover este comentário?')) return;

    try {
        const response = await fetch(`/api/comentarios/${comentarioId}`, { method: 'DELETE' });
        if (response.ok) {
            exibirAlerta('Comentário excluído com sucesso.', 'success');
            carregarComentarios(noticiaId);
        } else {
            const data = await response.json();
            exibirAlerta(data.error || 'Erro ao excluir comentário.', 'danger');
        }
    } catch (e) {
        exibirAlerta('Erro de conexão ao excluir comentário.', 'danger');
    }
}

// Utilitários de Compartilhamento
function compartilharNoticia(botao) {
    const noticia = botao.closest('.noticia');
    const menu = noticia.querySelector('.menu-compartilhar');
    document.querySelectorAll('.menu-compartilhar.aberto').forEach(m => {
        if (m !== menu) m.classList.remove('aberto');
    });
    menu.classList.toggle('aberto');
}

function obterDadosCompartilhamento(elemento) {
    const noticia = elemento.closest('.noticia');
    return {
        titulo: noticia.querySelector('h2').innerText,
        texto: noticia.querySelector('.card-text').innerText,
        url: window.location.href
    };
}

function compartilharWhatsApp(e, elemento) {
    e.preventDefault();
    const d = obterDadosCompartilhamento(elemento);
    const msg = encodeURIComponent(`${d.titulo}\n\n${d.texto.substring(0, 100)}...\n\nConfira: ${d.url}`);
    window.open(`https://wa.me/?text=${msg}`, '_blank');
}

function compartilharFacebook(e, elemento) {
    e.preventDefault();
    const url = encodeURIComponent(obterDadosCompartilhamento(elemento).url);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=700,height=500');
}

function compartilharX(e, elemento) {
    e.preventDefault();
    const d = obterDadosCompartilhamento(elemento);
    const text = encodeURIComponent(`${d.titulo} - ${d.url}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'width=700,height=500');
}

function copiarLinkNoticia(elemento) {
    const url = window.location.href;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
            exibirAlerta('Link da notícia copiado para a área de transferência!', 'success');
        });
    } else {
        alert('Não foi possível copiar o link automaticamente.');
    }
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[tag] || tag));
}

function escapeJS(str) {
    if (!str) return '';
    return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
}
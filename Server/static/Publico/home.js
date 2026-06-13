document.addEventListener('DOMContentLoaded', () => {
    carregarNoticias();
    carregarOngs();
});

// Busca e renderiza as últimas notícias cadastrados no banco
async function carregarNoticias() {
    const container = document.getElementById('container-noticias');
    try {
        const response = await fetch('/api/noticias?limit=5');
        const resultado = await response.json();

        if (response.ok && resultado.success && resultado.data.length > 0) {
            container.innerHTML = '';
            resultado.data.forEach(noticia => {
                const dataFormatada = noticia.data_hora 
                    ? new Date(noticia.data_hora).toLocaleDateString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })
                    : 'Data não informada';

                // Trata quebras de linha no corpo da notícia para exibição adequada no HTML
                const corpoFormatado = noticia.corpo.replace(/\n/g, '<br>');

                const cardHtml = `
                    <div class="col-12">
                        <div class="card border-0 shadow-sm p-4 mb-2 bg-white" style="border-radius: 12px;">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="badge text-white" style="background-color: #7a4b00; font-size: 0.75rem;">Notícia</span>
                                <small class="text-muted"><i class="bi bi-clock"></i> ${dataFormatada}</small>
                            </div>
                            <h4 class="h5 fw-bold mb-3" style="color: #7a4b00;">${escapeHTML(noticia.titulo)}</h4>
                            <p class="card-text text-secondary mb-0" style="line-height: 1.6; font-size: 0.95rem;">
                                ${corpoFormatado}
                            </p>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', cardHtml);
            });
        } else {
            container.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="bi bi-newspaper fs-1"></i>
                    <p class="mt-2 mb-0">Nenhuma notícia publicada no momento.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar notícias:', error);
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                Erro ao conectar com a API de notícias.
            </div>
        `;
    }
}

// Busca e renderiza as ONGs parceiras cadastradas no banco
async function carregarOngs() {
    const container = document.getElementById('container-ongs');
    try {
        const response = await fetch('/api/ongs?limit=5');
        const resultado = await response.json();

        if (response.ok && resultado.success && resultado.data.length > 0) {
            container.innerHTML = '';
            resultado.data.forEach(ong => {
                const siteHtml = ong.site 
                    ? `<p class="mb-1 text-truncate"><i class="bi bi-globe text-brand"></i> <a href="${escapeHTML(ong.site)}" target="_blank" class="text-decoration-none text-secondary">${escapeHTML(ong.site)}</a></p>`
                    : '';
                const enderecoHtml = ong.endereco_fisico
                    ? `<p class="mb-1 text-secondary small"><i class="bi bi-geo-alt-fill text-brand"></i> ${escapeHTML(ong.endereco_fisico)}</p>`
                    : '';

                const cardHtml = `
                    <div class="col-12">
                        <div class="card border-0 shadow-sm p-4 mb-2 bg-white" style="border-radius: 12px; border-left: 5px solid #7a4b00 !important;">
                            <h5 class="fw-bold mb-3" style="color: #7a4b00;">${escapeHTML(ong.nome_instituicao)}</h5>
                            
                            <div class="mb-3">
                                ${enderecoHtml}
                                ${siteHtml}
                            </div>

                            <div class="d-flex flex-column gap-2">
                                <div class="input-group input-group-sm">
                                    <span class="input-group-text bg-light text-secondary border-end-0" style="font-size: 0.75rem;">PIX</span>
                                    <input type="text" class="form-control bg-light border-start-0 text-secondary" style="font-size: 0.75rem;" readonly value="${escapeHTML(ong.pix_doacao)}" id="pix-${ong.id}">
                                    <button class="btn btn-outline-brand text-brand" type="button" onclick="copiarPix('${ong.pix_doacao}', ${ong.id})" id="btn-pix-${ong.id}" style="border-color: rgba(122, 75, 0, 0.4); font-size: 0.75rem;">
                                        <i class="bi bi-copy"></i> Copiar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', cardHtml);
            });
        } else {
            container.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="bi bi-heart fs-1 text-danger"></i>
                    <p class="mt-2 mb-0">Nenhuma ONG parceira cadastrada no momento.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar ONGs:', error);
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                Erro ao conectar com a API de ONGs.
            </div>
        `;
    }
}

// Copia o valor da chave PIX para a área de transferência do usuário com feedback dinâmico
function copiarPix(chave, id) {
    navigator.clipboard.writeText(chave).then(() => {
        const btn = document.getElementById(`btn-pix-${id}`);
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check-lg text-success"></i> Copiado!';
        btn.classList.add('bg-success-subtle');
        setTimeout(() => {
            btn.innerHTML = originalContent;
            btn.classList.remove('bg-success-subtle');
        }, 2000);
    }).catch(err => {
        console.error('Erro ao copiar chave PIX:', err);
    });
}

// Auxiliar para evitar injeção XSS
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

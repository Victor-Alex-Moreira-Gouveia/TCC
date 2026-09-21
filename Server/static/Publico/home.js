document.addEventListener('DOMContentLoaded', () => {
    carregarNoticias();
});

// Busca e renderiza as notícias cadastradas
async function carregarNoticias() {
    const container = document.getElementById('container-noticias');
    if (!container) return;
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

                const corpoFormatado = noticia.corpo ? escapeHTML(noticia.corpo).replace(/\n/g, '<br>') : '';

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

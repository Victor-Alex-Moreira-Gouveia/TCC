document.addEventListener('DOMContentLoaded', () => {
    carregarNoticiasPreview();
    carregarAnimaisEncontradosPreview();
});

async function carregarNoticiasPreview() {
    const container = document.getElementById('container-noticias-preview');
    if (!container) return;

    try {
        const response = await fetch('/api/preview/noticias');
        const resultado = await response.json();
        if (!response.ok || !resultado.success) {
            throw new Error('Não foi possível carregar as notícias.');
        }

        const noticias = Array.isArray(resultado.data) ? resultado.data : [];
        renderizarPreview(container, noticias, criarCardNoticiaPreview, 'Nenhuma notícia publicada no momento.');
    } catch (error) {
        console.error('Erro ao carregar notícias:', error);
        mostrarMensagemPreview(container, 'Não foi possível carregar as notícias agora.');
    }
}

async function carregarAnimaisEncontradosPreview() {
    const container = document.getElementById('container-animais-encontrados');
    if (!container) return;

    try {
        const response = await fetch('/api/preview/animais-encontrados');
        const resultado = await response.json();
        if (!response.ok || !resultado.success) {
            throw new Error('Não foi possível carregar os animais encontrados.');
        }

        const animais = Array.isArray(resultado.data) ? resultado.data : [];
        renderizarPreview(container, animais, criarCardAnimalEncontradoPreview, 'Ainda não há animais marcados como encontrados.');
    } catch (error) {
        console.error('Erro ao carregar animais encontrados:', error);
        mostrarMensagemPreview(container, 'Não foi possível carregar os animais encontrados agora.');
    }
}

function renderizarPreview(container, itens, criarCard, mensagemVazia) {
    container.replaceChildren();
    container.setAttribute('aria-busy', 'false');

    if (itens.length === 0) {
        mostrarMensagemPreview(container, mensagemVazia);
        return;
    }

    itens.forEach(item => container.appendChild(criarCard(item)));
}

function mostrarMensagemPreview(container, mensagem) {
    const coluna = document.createElement('div');
    coluna.className = 'col-12';

    const texto = document.createElement('p');
    texto.className = 'home-preview-feedback';
    texto.textContent = mensagem;
    coluna.appendChild(texto);

    container.replaceChildren(coluna);
    container.setAttribute('aria-busy', 'false');
}

function criarCardNoticiaPreview(noticia) {
    const coluna = criarColunaPreview('col-12 col-md-6 col-xl-4');
    const card = criarCardBasePreview();

    const topo = document.createElement('div');
    topo.className = 'home-preview-card-top';

    const icone = document.createElement('span');
    icone.className = 'home-preview-card-icon';
    icone.setAttribute('aria-hidden', 'true');
    icone.innerHTML = '<i class="bi bi-heart-pulse-fill"></i>';

    const categoria = document.createElement('span');
    categoria.className = 'home-preview-label';
    categoria.textContent = 'Notícia';
    topo.append(icone, categoria);

    const titulo = criarTituloPreview(noticia.titulo || 'Notícia');
    const resumo = criarResumoPreview(noticia.resumo || 'Acesse para conferir esta atualização.');
    card.append(topo, titulo, resumo);

    const data = formatarDataPreview(noticia.data_hora);
    if (data) card.appendChild(criarDetalhePreview('bi-clock', data, 'home-preview-card-date'));

    coluna.appendChild(card);
    return coluna;
}

function criarCardAnimalEncontradoPreview(animal) {
    const coluna = criarColunaPreview('col-12 col-md-6 col-xl-4');
    const card = criarCardBasePreview();

    if (animal.imagem_url) {
        const imagem = document.createElement('img');
        imagem.className = 'home-found-image';
        imagem.src = animal.imagem_url;
        imagem.alt = `Foto de ${animal.nome || 'animal encontrado'}`;
        imagem.loading = 'lazy';
        card.appendChild(imagem);
    } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'home-found-image-placeholder';
        placeholder.setAttribute('aria-hidden', 'true');
        placeholder.innerHTML = '<i class="bi bi-paw-fill"></i>';
        card.appendChild(placeholder);
    }

    const status = document.createElement('span');
    status.className = 'home-found-status';
    status.textContent = 'Encontrado';

    const titulo = criarTituloPreview(animal.nome || 'Animal encontrado');
    const especie = criarDetalhePreview('bi-tag-fill', animal.especie || 'Espécie não informada', 'home-found-detail');
    const local = criarDetalhePreview('bi-geo-alt-fill', animal.local || 'Local não informado', 'home-found-detail');
    const resumo = criarResumoPreview(animal.resumo || 'Sem descrição adicional.');

    card.append(status, titulo, especie, local, resumo);

    const data = formatarDataPreview(animal.data_ocorrido);
    if (data) card.appendChild(criarDetalhePreview('bi-calendar-event-fill', `Visto em ${data}`, 'home-preview-card-date'));

    coluna.appendChild(card);
    return coluna;
}

function criarColunaPreview(className) {
    const coluna = document.createElement('div');
    coluna.className = className;
    return coluna;
}

function criarCardBasePreview() {
    const card = document.createElement('article');
    card.className = 'home-preview-card h-100';
    return card;
}

function criarTituloPreview(texto) {
    const titulo = document.createElement('h3');
    titulo.className = 'home-preview-card-title';
    titulo.textContent = texto;
    return titulo;
}

function criarResumoPreview(texto) {
    const resumo = document.createElement('p');
    resumo.className = 'home-preview-card-summary';
    resumo.textContent = texto;
    return resumo;
}

function criarDetalhePreview(iconeNome, texto, className) {
    const detalhe = document.createElement('p');
    detalhe.className = className;

    const icone = document.createElement('i');
    icone.className = `bi ${iconeNome} me-1`;
    icone.setAttribute('aria-hidden', 'true');
    detalhe.append(icone, document.createTextNode(texto));
    return detalhe;
}

function formatarDataPreview(valor) {
    if (!valor) return '';
    const [ano, mes, dia] = String(valor).slice(0, 10).split('-');
    return ano && mes && dia ? `${dia}/${mes}/${ano}` : '';
}

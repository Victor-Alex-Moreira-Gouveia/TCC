function curtir(botao, idContador) {
    const contador = document.getElementById(idContador);
    const quantidade = parseInt(contador.innerText, 10);
    botao.classList.toggle('ativo');
    contador.innerText = botao.classList.contains('ativo') ? quantidade + 1 : quantidade - 1;
}

function mostrarComentarios(idComentario) {
    document.getElementById(idComentario).classList.toggle('aberto');
}

function compartilharNoticia(botao) {
    const noticia = botao.closest('.noticia');
    const menu = noticia.querySelector('.menu-compartilhar');
    document.querySelectorAll('.menu-compartilhar.aberto').forEach((outroMenu) => {
        if (outroMenu !== menu) outroMenu.classList.remove('aberto');
    });
    menu.classList.toggle('aberto');

    if (navigator.share && window.innerWidth <= 768) {
        navigator.share({
            title: noticia.querySelector('h2').innerText,
            text: noticia.querySelector('p').innerText,
            url: window.location.href
        }).catch(() => {});
    }
}

function obterDadosCompartilhamento(elemento) {
    const noticia = elemento.closest('.noticia');
    return {
        titulo: noticia.querySelector('h2').innerText,
        texto: noticia.querySelector('p').innerText,
        url: window.location.href
    };
}

function compartilharWhatsApp(event, elemento) {
    event.preventDefault();
    const dados = obterDadosCompartilhamento(elemento);
    const mensagem = encodeURIComponent(`${dados.titulo}\n\n${dados.texto}\n\nConfira: ${dados.url}`);
    window.open(`https://wa.me/?text=${mensagem}`, '_blank');
}

function compartilharFacebook(event, elemento) {
    event.preventDefault();
    const url = encodeURIComponent(obterDadosCompartilhamento(elemento).url);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=700,height=500');
}

function compartilharX(event, elemento) {
    event.preventDefault();
    const dados = obterDadosCompartilhamento(elemento);
    const texto = encodeURIComponent(`${dados.titulo} - ${dados.url}`);
    window.open(`https://twitter.com/intent/tweet?text=${texto}`, '_blank', 'width=700,height=500');
}

function copiarLinkNoticia(elemento) {
    const url = obterDadosCompartilhamento(elemento).url;
    if (!navigator.clipboard) {
        alert('Seu navegador não permite copiar o link automaticamente.');
        return;
    }
    navigator.clipboard.writeText(url)
        .then(() => alert('Link da notícia copiado! Agora é só colar onde quiser.'))
        .catch(() => alert('Não foi possível copiar o link automaticamente.'));
}

function adicionarComentario(idLista, idInput, idContador) {
    const input = document.getElementById(idInput);
    const texto = input.value.trim();
    if (texto === '') return;

    const comentario = document.createElement('div');
    comentario.className = 'comentario';
    comentario.innerHTML = `<strong>Anônimo 🐾:</strong> ${texto}`;
    document.getElementById(idLista).appendChild(comentario);

    const contador = document.getElementById(idContador);
    contador.innerText = parseInt(contador.innerText, 10) + 1;
    input.value = '';
}
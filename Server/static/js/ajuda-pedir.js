const instrucoesUrgencia = {
    'Ferimento grave': 'Mantenha a calma e evite movimentos bruscos no animal para não piorar a lesão. Pressione um pano limpo levemente sobre o sangramento. <strong>Ligue imediatamente para um veterinário de plantão ou serviço de resgate animal</strong> e prepare um transporte seguro.',
    'Engasgo': 'Abra a boca do animal com cuidado para verificar se há objeto visível (remova apenas se for fácil alcançá-lo sem empurrar para dentro). Em pets de menor porte, faça manobras leves com a cabeça para baixo. <strong>Ligue para uma clínica veterinária 24h ou leve-o imediatamente</strong>.',
    'Convulsão': 'Afaste móveis e objetos cortantes ou pesados ao redor para evitar traumas físicos. <strong>NÃO coloque as mãos ou objetos na boca do animal</strong> (alto risco de mordida e asfixia). Cronometre o tempo da crise e <strong>ligue para um veterinário</strong> para orientações de sedação ou transporte.',
    'Doença contagiosa': 'Isole o animal de outros pets e pessoas imediatamente para evitar contágio em massa. Utilize luvas, avental e máscara de proteção ao manuseá-lo. <strong>Ligue para a vigilância sanitária ou veterinário responsável</strong> para quarentena.',
    'Envenenamento': '<strong>NÃO induza o vômito</strong> por conta própria, pois substâncias corrosivas podem queimar ainda mais o esôfago. Guarde a embalagem ou uma amostra do veneno/alimento ingerido se possível. <strong>Ligue imediatamente para o Disque-Intoxicação ou leve-o a uma clínica urgente</strong>.',
    'Atropelamento': 'Não puxe o animal pelas patas ou pela cauda. Utilize uma superfície rígida (como uma tábua) ou um lençol esticado como maca improvisada para movê-lo com extremo cuidado. <strong>Ligue para o resgate veterinário, zoonoses ou polícia ambiental</strong>.',
    'Queimaduras ou exposição a produtos químicos': '<strong>NÃO aplique pomadas, manteiga ou gelo</strong> diretamente na lesão. Se for produto químico líquido, lave com água corrente em abundância. <strong>Procure atendimento veterinário emergencial imediatamente</strong>.'
};

const checkboxUrgencia = document.getElementById('checkbox-urgencia');
const selectUrgencia = document.getElementById('nivel_urgencia');
const guidanceBox = document.getElementById('urgencia-guidance-box');
const spanTituloAlerta = document.getElementById('urgencia-titulo-alerta');
const pTextoAlerta = document.getElementById('urgencia-texto-alerta');

function atualizarCondutaImediata() {
    if (checkboxUrgencia.checked) {
        const nivel = selectUrgencia.value;
        spanTituloAlerta.textContent = nivel;
        pTextoAlerta.innerHTML = instrucoesUrgencia[nivel] || 'Siga as orientações veterinárias de emergência padrão.';
        guidanceBox.classList.remove('d-none');
    } else {
        guidanceBox.classList.add('d-none');
    }
}

checkboxUrgencia.addEventListener('change', atualizarCondutaImediata);
selectUrgencia.addEventListener('change', () => {
    if (checkboxUrgencia.checked) atualizarCondutaImediata();
});

document.getElementById('formAjuda').addEventListener('submit', async (event) => {
    event.preventDefault();
    const alertMsg = document.getElementById('alert-message');
    alertMsg.classList.add('d-none');
    alertMsg.classList.remove('alert-danger', 'alert-success');

    const titulo = document.getElementById('titulo').value.trim();
    const corpo = document.getElementById('corpo').value.trim();
    const pixDoacao = document.getElementById('pix').value.trim();
    const tipoDenuncia = document.getElementById('tipo_denuncia').value.trim();
    const nivelUrgencia = document.getElementById('nivel_urgencia').value.trim();

    if (!titulo || !corpo || !pixDoacao) {
        alertMsg.textContent = 'Preencha título, relato e chave PIX antes de enviar.';
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch('/api/ajuda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo, corpo, pix_doacao: pixDoacao, tipo_denuncia: tipoDenuncia, nivel_urgencia: nivelUrgencia })
        });
        const dados = await response.json();

        if (response.ok) {
            alertMsg.textContent = 'Pedido de ajuda / denúncia enviado com sucesso! A comunidade foi notificada.';
            alertMsg.classList.add('alert-success');
            alertMsg.classList.remove('d-none');
            document.getElementById('formAjuda').reset();
            document.getElementById('tipo_denuncia').value = 'Animal doméstico';
            document.getElementById('nivel_urgencia').value = 'Ferimento grave';
            guidanceBox.classList.add('d-none');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            let message = dados.error || 'Erro ao enviar pedido de ajuda.';
            if (dados.details) message += ` (${Object.values(dados.details).join(' | ')})`;
            alertMsg.textContent = message;
            alertMsg.classList.add('alert-danger');
            alertMsg.classList.remove('d-none');
        }
    } catch (error) {
        alertMsg.textContent = 'Erro de conexão com o servidor.';
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
    }
});
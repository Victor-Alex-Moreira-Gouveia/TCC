const instrucoesUrgencia = {
    'Ferimento grave': 'Mantenha a calma e evite movimentos bruscos no animal para não piorar a lesão. Pressione um pano limpo levemente sobre o sangramento. <strong>Ligue imediatamente para um veterinário de plantão ou serviço de resgate animal</strong> e prepare um transporte seguro.',
    'Engasgo': 'Abra a boca do animal com cuidado para verificar se há objeto visível (remova apenas se for fácil alcançá-lo sem empurrar para dentro). Em pets de menor porte, faça manobras leves com a cabeça para baixo. <strong>Ligue para uma clínica veterinária 24h ou leve-o imediatamente</strong>.',
    'Convulsão': 'Afaste móveis e objetos cortantes ou pesados ao redor para evitar traumas físicos. <strong>NÃO coloque as mãos ou objetos na boca do animal</strong>. Cronometre o tempo da crise e ligue para um veterinário.',
    'Doença contagiosa': 'Isole o animal de outros pets e pessoas imediatamente para evitar contágio. Utilize luvas e máscara ao manuseá-lo. <strong>Ligue para a vigilância sanitária ou veterinário responsável</strong>.',
    'Envenenamento': '<strong>NÃO induza o vômito</strong> por conta própria. Guarde a embalagem ou amostra do veneno/alimento ingerido. <strong>Ligue imediatamente para o atendimento emergencial veterinário</strong>.',
    'Atropelamento': 'Não puxe o animal pelas patas ou pela cauda. Utilize uma superfície rígida ou lençol esticado como maca improvisada. <strong>Ligue para o resgate veterinário, zoonoses ou polícia ambiental</strong>.',
    'Queimaduras ou exposição a produtos químicos': '<strong>NÃO aplique pomadas, manteiga ou gelo</strong> na lesão. Se for produto químico líquido, lave com água corrente em abundância. <strong>Procure atendimento veterinário emergencial imediatamente</strong>.'
};

const checkboxUrgencia = document.getElementById('checkbox-urgencia');
const selectUrgencia = document.getElementById('nivel_urgencia');
const guidanceBox = document.getElementById('urgencia-guidance-box');
const spanTituloAlerta = document.getElementById('urgencia-titulo-alerta');
const pTextoAlerta = document.getElementById('urgencia-texto-alerta');

function atualizarCondutaImediata() {
    if (checkboxUrgencia && checkboxUrgencia.checked) {
        const nivel = selectUrgencia ? selectUrgencia.value : '';
        spanTituloAlerta.textContent = nivel;
        pTextoAlerta.innerHTML = instrucoesUrgencia[nivel] || 'Siga as orientações veterinárias de emergência padrão.';
        guidanceBox.classList.remove('d-none');
    } else {
        if (guidanceBox && !guidanceBox.dataset.persist) {
            guidanceBox.classList.add('d-none');
        }
    }
}

if (checkboxUrgencia) {
    checkboxUrgencia.addEventListener('change', () => {
        if (guidanceBox) delete guidanceBox.dataset.persist;
        atualizarCondutaImediata();
    });
}

if (selectUrgencia) {
    selectUrgencia.addEventListener('change', () => {
        if (checkboxUrgencia && checkboxUrgencia.checked) {
            atualizarCondutaImediata();
        }
    });
}

document.getElementById('formAjuda').addEventListener('submit', async (event) => {
    event.preventDefault();
    const alertMsg = document.getElementById('alert-message');
    alertMsg.classList.add('d-none');
    alertMsg.classList.remove('alert-danger', 'alert-success');

    const titulo = document.getElementById('titulo').value.trim();
    const corpo = document.getElementById('corpo').value.trim();
    const tipoDenuncia = document.getElementById('tipo_denuncia').value.trim();
    const nivelUrgencia = document.getElementById('nivel_urgencia').value.trim();

    if (!titulo || !corpo) {
        alertMsg.textContent = 'Preencha o título e a descrição da denúncia antes de enviar.';
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch('/api/ajuda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                titulo,
                corpo,
                tipo_denuncia: tipoDenuncia,
                nivel_urgencia: nivelUrgencia
            })
        });
        const dados = await response.json();

        if (response.ok && dados.success) {
            alertMsg.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${dados.message || 'Denúncia registrada com sucesso.'}`;
            alertMsg.classList.add('alert-success');
            alertMsg.classList.remove('d-none');

            // Exibe a orientação imediata retornada pelo backend
            const orientacao = (dados.data && dados.data.orientacao_imediata)
                || instrucoesUrgencia[nivelUrgencia]
                || 'Caso de emergência: contate assistência veterinária ou autoridade local.';

            spanTituloAlerta.textContent = nivelUrgencia;
            pTextoAlerta.innerHTML = orientacao;
            guidanceBox.dataset.persist = "true";
            guidanceBox.classList.remove('d-none');

            document.getElementById('formAjuda').reset();
            document.getElementById('tipo_denuncia').value = 'Animal doméstico';
            document.getElementById('nivel_urgencia').value = 'Ferimento grave';

            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            let message = dados.error || 'Erro ao registrar denúncia.';
            if (dados.details) {
                const det = typeof dados.details === 'object' ? Object.values(dados.details).join(' | ') : dados.details;
                message += ` (${det})`;
            }
            alertMsg.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> ${message}`;
            alertMsg.classList.add('alert-danger');
            alertMsg.classList.remove('d-none');
        }
    } catch (error) {
        alertMsg.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-2"></i> Erro de conexão com o servidor ao salvar denúncia.';
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
    }
});
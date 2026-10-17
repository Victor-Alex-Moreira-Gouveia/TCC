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
const PENDING_SUBMISSION_KEY = 'ajuda:pending-submission';
let pendingSubmissionInMemory = null;

function atualizarCondutaImediata() {
    if (checkboxUrgencia && checkboxUrgencia.checked && guidanceBox && spanTituloAlerta && pTextoAlerta) {
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

function showAlert(alertMsg, message, style) {
    if (!alertMsg) return;
    alertMsg.textContent = message;
    alertMsg.classList.remove('d-none', 'alert-danger', 'alert-success');
    alertMsg.classList.add(style);
}

function criarIdempotencyKey() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
        return window.crypto.randomUUID();
    }
    if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
        const bytes = window.crypto.getRandomValues(new Uint8Array(16));
        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (char) => {
        const random = Math.random() * 16 | 0;
        return (char === 'x' ? random : (random & 0x3 | 0x8)).toString(16);
    });
}

function lerEnvioPendente() {
    if (pendingSubmissionInMemory) return pendingSubmissionInMemory;
    try {
        return JSON.parse(sessionStorage.getItem(PENDING_SUBMISSION_KEY) || 'null');
    } catch (_) {
        return null;
    }
}

function salvarEnvioPendente(envio) {
    pendingSubmissionInMemory = envio;
    try {
        sessionStorage.setItem(PENDING_SUBMISSION_KEY, JSON.stringify(envio));
    } catch (_) {
        // The API still receives an idempotency key for this page lifetime.
    }
}

function limparEnvioPendente() {
    pendingSubmissionInMemory = null;
    try { sessionStorage.removeItem(PENDING_SUBMISSION_KEY); } catch (_) { /* unavailable storage */ }
}

async function reconciliarEnvio(idempotencyKey) {
    try {
        const response = await fetch(`/api/ajuda/confirmar/${encodeURIComponent(idempotencyKey)}`, {
            headers: { 'Accept': 'application/json' },
            cache: 'no-store'
        });
        let data = null;
        try { data = await response.json(); } catch (_) { /* handled as unknown below */ }
        if (response.ok && data && data.success && data.data) {
            return { found: true, id: data.data.id };
        }
        if (response.status === 404) return { found: false };
        return { found: false, unknown: true };
    } catch (_) {
        return { found: false, unknown: true };
    }
}

function exibirOrientacao(nivelUrgencia, orientacao) {
    if (!guidanceBox || !spanTituloAlerta || !pTextoAlerta) return;
    spanTituloAlerta.textContent = nivelUrgencia;
    pTextoAlerta.innerHTML = orientacao || instrucoesUrgencia[nivelUrgencia] ||
        'Caso de emergência: contate assistência veterinária ou autoridade local.';
    guidanceBox.dataset.persist = 'true';
    guidanceBox.classList.remove('d-none');
}

function confirmarSucesso(alertMsg, form, nivelUrgencia, dados, resetForm = true) {
    showAlert(alertMsg, 'Denúncia registrada com sucesso.', 'alert-success');
    try {
        exibirOrientacao(nivelUrgencia, dados && dados.orientacao_imediata);
        if (resetForm && form) {
            form.reset();
            document.getElementById('tipo_denuncia').value = 'Animal doméstico';
            document.getElementById('nivel_urgencia').value = 'Ferimento grave';
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (_) {
        // A successful persistence response remains successful if optional UI updates fail.
    }
}

document.getElementById('formAjuda').addEventListener('submit', async (event) => {
    event.preventDefault();
    const alertMsg = document.getElementById('alert-message');
    alertMsg.classList.add('d-none');
    alertMsg.classList.remove('alert-danger', 'alert-success');
    alertMsg.textContent = '';

    const titulo = document.getElementById('titulo').value.trim();
    const corpo = document.getElementById('corpo').value.trim();
    const tipoDenuncia = document.getElementById('tipo_denuncia').value.trim();
    const nivelUrgencia = document.getElementById('nivel_urgencia').value.trim();

    if (!titulo || !corpo) {
        showAlert(alertMsg, 'Preencha o título e a descrição da denúncia antes de enviar.', 'alert-danger');
        return;
    }

    const form = document.getElementById('formAjuda');
    const submitButton = form.querySelector('[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando…';

    const payload = { titulo, corpo, tipo_denuncia: tipoDenuncia, nivel_urgencia: nivelUrgencia };
    const pending = lerEnvioPendente();
    const idempotencyKey = pending?.idempotency_key || criarIdempotencyKey();
    salvarEnvioPendente({ idempotency_key: idempotencyKey, payload });
    let response = null;
    let dados = null;

    try {
        response = await fetch('/api/ajuda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({ ...payload, idempotency_key: idempotencyKey })
        });
        try { dados = await response.json(); } catch (_) { /* reconcile below */ }

        if (response.ok && dados && dados.success) {
            limparEnvioPendente();
            confirmarSucesso(alertMsg, form, nivelUrgencia, dados.data);
            return;
        }

        if (response.status >= 500 || !dados || response.status === 409) {
            const confirmacao = await reconciliarEnvio(idempotencyKey);
            if (confirmacao.found) {
                limparEnvioPendente();
                const dadosIguais = JSON.stringify(pending?.payload || payload) === JSON.stringify(payload);
                confirmarSucesso(alertMsg, form, nivelUrgencia, null, dadosIguais);
                if (!dadosIguais) {
                    showAlert(
                        alertMsg,
                        'Uma denúncia anterior foi confirmada. Os dados que estão no formulário agora não foram enviados; confira o registro antes de enviar outra denúncia.',
                        'alert-success'
                    );
                }
                return;
            }
            showAlert(
                alertMsg,
                'Ainda não foi possível confirmar o resultado. Não envie outra denúncia com um novo formulário: tente novamente; a mesma chave impede duplicação.',
                'alert-danger'
            );
            return;
        }

        limparEnvioPendente();
        let message = (dados && dados.error) || `Erro ao registrar denúncia (HTTP ${response.status}).`;
        if (dados && dados.details) {
            const det = typeof dados.details === 'object'
                ? Object.values(dados.details).join(' | ')
                : String(dados.details);
            message += ` (${det})`;
        }
        showAlert(alertMsg, message, 'alert-danger');
    } catch (_) {
        const confirmacao = await reconciliarEnvio(idempotencyKey);
        if (confirmacao.found) {
            limparEnvioPendente();
            confirmarSucesso(alertMsg, form, nivelUrgencia, null);
        } else {
            showAlert(
                alertMsg,
                'A confirmação ainda não chegou. Sua tentativa está protegida contra duplicação; tente enviar novamente para confirmar o mesmo registro.',
                'alert-danger'
            );
        }
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

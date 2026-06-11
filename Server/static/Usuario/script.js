const BASE = '/api/usuarios';

/**
 * Exibe mensagens de resposta do servidor de forma segura no console visual (#log)
 * ou redireciona para o console do navegador caso o elemento não exista.
 */
function log(message) {
    const logElement = document.getElementById('log');
    
    if (logElement) {
        // Se a mensagem for um objeto JSON vindo do backend, formata para texto legível
        if (typeof message === 'object') {
            logElement.textContent = JSON.stringify(message, null, 2);
        } else {
            logElement.textContent = message;
        }
    } else {
        console.log("Log do Servidor:", message);
    }
}

/**
 * Centraliza e padroniza as requisições Fetch da API
 */
async function apiFetch(url, opts = {}) {
    try {
        const r = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            ...opts
        });
        
        if (r.status === 204) {
            return { success: true, message: 'Removido com sucesso.' };
        }
        
        return await r.json();
    } catch (error) {
        return { success: false, message: 'Erro ao conectar com o servidor.' };
    }
}

/**
 * CRUD: Criação de Usuário
 */
async function createUsuario() {
    const nomeInput = document.getElementById('c-nome');
    const emailInput = document.getElementById('c-email');
    const senhaInput = document.getElementById('c-senha');

    const body = {
        nome_usuario: nomeInput.value.trim(),
        email: emailInput.value.trim(),
        senha: senhaInput.value.trim(),
    };

    if (!body.nome_usuario || !body.email || !body.senha) {
        log('Erro: Todos os campos são obrigatórios para o cadastro.');
        return;
    }

    const res = await apiFetch(BASE, { method: 'POST', body: JSON.stringify(body) });
    log(res);

    if (res.success || r.status === 201 || res.id) { // Adaptado para checar sucesso de forma ampla
        loadUsuarios();
        // Limpa os campos após o sucesso
        nomeInput.value = '';
        emailInput.value = '';
        senhaInput.value = '';
    }
}

/**
 * CRUD: Leitura/Listagem de Usuários
 */
async function loadUsuarios() {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return; // Proteção caso a tabela sumpa por algum motivo

    const res = await apiFetch(BASE);
    
    // Se o backend retornar erro ou não for uma lista, avisa no console
    if (!Array.isArray(res)) {
        log(res);
        return;
    }

    tbody.innerHTML = ''; // Limpa as linhas antigas

    res.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${u.id}</td>
            <td>${u.nome_usuario}</td>
            <td>${u.email}</td>
            <td class="text-center">
                <div class="d-flex justify-content-center gap-2">
                    <button class="btn btn-sm btn-outline-brand" onclick="fillUpdate(${u.id}, '${u.nome_usuario}', '${u.email}')" title="Editar">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUsuario(${u.id})" title="Excluir">
                        <i class="bi bi-trash3"></i>
                    </button>
                </div>
            </td>`;
        tbody.appendChild(tr);
    });
}

/**
 * Auxiliar: Preenche o formulário de atualização ao clicar em editar
 */
function fillUpdate(id, nome, email) {
    const idInput = document.getElementById('u-id');
    const nomeInput = document.getElementById('u-nome');
    const emailInput = document.getElementById('u-email');
    const senhaInput = document.getElementById('u-senha');

    if (idInput) idInput.value = id;
    if (nomeInput) nomeInput.value = nome;
    if (emailInput) emailInput.value = email;
    if (senhaInput) senhaInput.value = '';

    // Efeito visual sutil para levar o Admin até o formulário
    idInput?.scrollIntoView({ behavior: 'smooth' });
}

/**
 * CRUD: Atualização de Usuário
 */
async function updateUsuario() {
    const id = document.getElementById('u-id').value;
    if (!id) { 
        log('Erro: Selecione um usuário na tabela clicando no botão editar antes de atualizar.'); 
        return; 
    }

    const body = {};
    const nome = document.getElementById('u-nome').value.trim();
    const email = document.getElementById('u-email').value.trim();
    const senha = document.getElementById('u-senha').value.trim();

    if (nome)  body.nome_usuario = nome;
    if (email) body.email = email;
    if (senha) body.senha = senha;

    const res = await apiFetch(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(body) });
    log(res);
    
    loadUsuarios();
}

/**
 * CRUD: Exclusão de Usuário
 */
async function deleteUsuario(id) {
    if (!confirm(`Deseja remover permanentemente o usuário ID ${id}?`)) return;
    
    const res = await apiFetch(`${BASE}/${id}`, { method: 'DELETE' });
    log(res);
    
    loadUsuarios();
}

/**
 * Auxiliar: Limpa o painel de log visual
 */
function clearLog() {
    const logElement = document.getElementById('log');
    if (logElement) logElement.textContent = '— pronto para monitorar requisições —';
}

/**
 * INICIALIZAÇÃO SEGURA
 * Garante que o script só rode funções automáticas após o DOM/HTML estar 100% pronto na tela.
 */
document.addEventListener('DOMContentLoaded', () => {
    loadUsuarios();
});
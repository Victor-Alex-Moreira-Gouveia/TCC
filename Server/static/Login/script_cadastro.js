document.getElementById('formCadastro').addEventListener('submit', async (e) => {
    e.preventDefault();
    const alertMsg = document.getElementById('alert-message');
    alertMsg.classList.add('d-none');
    alertMsg.classList.remove('alert-danger', 'alert-success');

    const nome_usuario = document.getElementById('nome_usuario').value.trim();
    const email = document.getElementById('email').value.trim();
    const senha = document.getElementById('senha').value.trim();

    if (senha.length < 8) {
        alertMsg.textContent = "A senha deve conter no mínimo 8 caracteres.";
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch('/api/usuarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome_usuario, email, senha })
        });

        const dados = await response.json();

        if (response.ok) {
            alertMsg.textContent = "Cadastro realizado com sucesso! Redirecionando para o login...";
            alertMsg.classList.add('alert-success');
            alertMsg.classList.remove('d-none');
            document.getElementById('formCadastro').reset();
            setTimeout(() => {
                window.location.href = '/test/login';
            }, 2000);
        } else {
            let msg = dados.error || "Erro ao realizar o cadastro.";
            if (dados.details) {
                const errors = Object.values(dados.details).join(' | ');
                msg += ` (${errors})`;
            }
            alertMsg.textContent = msg;
            alertMsg.classList.add('alert-danger');
            alertMsg.classList.remove('d-none');
        }
    } catch (error) {
        alertMsg.textContent = "Erro ao conectar com o servidor.";
        alertMsg.classList.add('alert-danger');
        alertMsg.classList.remove('d-none');
    }
});

document.getElementById('toggleSenha').addEventListener('click', function () {
    const inputSenha = document.getElementById('senha');
    const iconeOlho = document.getElementById('iconeOlho');

    if (inputSenha.type === 'password') {
        inputSenha.type = 'text';
        iconeOlho.classList.remove('bi-eye-slash');
        iconeOlho.classList.add('bi-eye'); // Mostra o olho aberto (senha visível)
    } else {
        inputSenha.type = 'password';
        iconeOlho.classList.remove('bi-eye');
        iconeOlho.classList.add('bi-eye-slash'); // Mostra o olho cortado (senha oculta)
    }
});
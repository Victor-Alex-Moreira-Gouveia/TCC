document.getElementById('formLogin').addEventListener('submit', async (e) => {
    e.preventDefault();
    const alertErro = document.getElementById('alert-erro');
    alertErro.classList.add('d-none');

    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });

        const dados = await response.json();

        if (response.ok) {
            window.location.href = dados.redirect;
        } else {
            alertErro.textContent = dados.mensagem;
            alertErro.classList.remove('d-none');
        }
    } catch (error) {
        alertErro.textContent = "Erro ao conectar com o servidor.";
        alertErro.classList.remove('d-none');
    }
});
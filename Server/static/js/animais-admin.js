(() => {
    const form = document.getElementById("formAdminAnimal");
    const tbody = document.getElementById("admin-animais-tbody");
    const vazio = document.getElementById("admin-vazio");
    const alerta = document.getElementById("admin-animal-alert");
    const fotoAtual = document.getElementById("admin-foto-atual");
    const inputImagem = document.getElementById("admin-imagem");

    let animais = [];

    function esc(valor) {
        return String(valor ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
        }[c]));
    }

    function dataPt(data) {
        if (!data) return "—";
        const [ano, mes, dia] = data.split("-");
        return (ano && mes && dia) ? `${dia}/${mes}/${ano}` : data;
    }

    function mostrarAlerta(texto, tipo = "success") {
        alerta.textContent = texto;
        alerta.className = `alert alert-${tipo}`;
        alerta.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function preencher(animal) {
        document.getElementById("admin-id").value = animal.id;
        document.getElementById("admin-nome").value = animal.nome || "";
        document.getElementById("admin-especie").value = animal.especie || "Outro";
        document.getElementById("admin-sexo").value = animal.sexo || "Não informado";
        document.getElementById("admin-status").value = animal.status || "Perdido";
        document.getElementById("admin-data").value = animal.data_ocorrido || "";
        document.getElementById("admin-local").value = animal.local || "";
        document.getElementById("admin-contato").value = animal.contato || "";
        document.getElementById("admin-descricao").value = animal.descricao || "";
        document.getElementById("admin-remover-imagem").checked = false;
        inputImagem.value = "";

        fotoAtual.innerHTML = animal.tem_imagem
            ? `<img class="animal-admin-thumb" src="/api/animais-perdidos/${animal.id}/imagem"
                    alt="Foto atual de ${esc(animal.nome)}">`
            : `<small class="text-muted">Este registro não possui foto.</small>`;

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function limparForm() {
        form.reset();
        document.getElementById("admin-id").value = "";
        document.getElementById("admin-especie").value = "Cachorro";
        document.getElementById("admin-sexo").value = "Não informado";
        document.getElementById("admin-status").value = "Perdido";
        fotoAtual.innerHTML = '<small class="text-muted">Selecione um registro para editar.</small>';
    }

    function renderizar() {
        if (!animais.length) {
            tbody.innerHTML = "";
            vazio.classList.remove("d-none");
            return;
        }

        vazio.classList.add("d-none");

        tbody.innerHTML = animais.map((animal) => `
            <tr>
                <td>${animal.id}</td>
                <td>
                    <strong>${esc(animal.nome)}</strong>
                    <div class="small text-muted">${esc(animal.especie)}</div>
                </td>
                <td>${esc(animal.local)}</td>
                <td>
                    <span class="animal-status ${animal.status === "Encontrado" ? "animal-status-found" : "animal-status-lost"}">
                        ${esc(animal.status)}
                    </span>
                </td>
                <td>${dataPt(animal.data_ocorrido)}</td>
                <td>${animal.tem_imagem ? '<i class="bi bi-image-fill text-brand fs-5"></i>' : '<span class="text-muted">—</span>'}</td>
                <td class="text-center">
                    <div class="d-flex gap-1 justify-content-center">
                        <button class="btn btn-sm btn-outline-primary" data-editar="${animal.id}" title="Editar">
                            <i class="bi bi-pencil-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" data-excluir="${animal.id}" title="Excluir">
                            <i class="bi bi-trash-fill"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");
    }

    async function carregar() {
        try {
            const response = await fetch("/api/animais-perdidos");
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || "Erro ao carregar.");
            }

            animais = Array.isArray(result.data) ? result.data : [];
            renderizar();
        } catch (error) {
            mostrarAlerta(error.message || "Não foi possível carregar os registros.", "danger");
        }
    }

    tbody.addEventListener("click", async (event) => {
        const editar = event.target.closest("[data-editar]");
        if (editar) {
            const animal = animais.find(
                (item) => String(item.id) === editar.dataset.editar
            );
            if (animal) preencher(animal);
            return;
        }

        const excluir = event.target.closest("[data-excluir]");
        if (!excluir) return;

        const id = excluir.dataset.excluir;
        const animal = animais.find((item) => String(item.id) === id);

        if (!animal) return;

        const confirmar = window.confirm(
            `Excluir o cadastro de "${animal.nome}"?`
        );

        if (!confirmar) return;

        try {
            const response = await fetch(`/api/animais-perdidos/${id}`, {
                method: "DELETE"
            });

            if (!response.ok && response.status !== 204) {
                const result = await response.json().catch(() => ({}));
                throw new Error(result.error || "Não foi possível excluir.");
            }

            mostrarAlerta("Cadastro excluído com sucesso.", "success");
            limparForm();
            await carregar();
        } catch (error) {
            mostrarAlerta(error.message || "Erro ao excluir.", "danger");
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const id = document.getElementById("admin-id").value;
        if (!id) {
            mostrarAlerta("Selecione um cadastro na tabela para editar.", "warning");
            return;
        }

        const button = document.getElementById("admin-salvar");
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...';

        try {
            const fd = new FormData();
            fd.append("nome", document.getElementById("admin-nome").value.trim());
            fd.append("especie", document.getElementById("admin-especie").value);
            fd.append("sexo", document.getElementById("admin-sexo").value);
            fd.append("status", document.getElementById("admin-status").value);
            fd.append("data_ocorrido", document.getElementById("admin-data").value);
            fd.append("local", document.getElementById("admin-local").value.trim());
            fd.append("contato", document.getElementById("admin-contato").value.trim());
            fd.append("descricao", document.getElementById("admin-descricao").value.trim());

            const imagem = inputImagem.files?.[0];
            if (imagem) {
                fd.append("imagem", imagem);
            }

            if (document.getElementById("admin-remover-imagem").checked) {
                fd.append("remover_imagem", "1");
            }

            const response = await fetch(`/api/animais-perdidos/${id}`, {
                method: "PUT",
                body: fd
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                const detalhes = result.details && typeof result.details === "object"
                    ? Object.values(result.details).join(" ")
                    : "";
                throw new Error(
                    [result.error || result.message || "Erro ao atualizar.", detalhes]
                        .filter(Boolean)
                        .join(" ")
                );
            }

            mostrarAlerta(result.message || "Cadastro atualizado com sucesso.", "success");
            limparForm();
            await carregar();
        } catch (error) {
            mostrarAlerta(error.message || "Não foi possível atualizar.", "danger");
        } finally {
            button.disabled = false;
            button.textContent = "Salvar alterações";
        }
    });

    document.getElementById("admin-limpar").addEventListener("click", limparForm);
    document.getElementById("admin-atualizar").addEventListener("click", carregar);

    limparForm();
    carregar();
})();

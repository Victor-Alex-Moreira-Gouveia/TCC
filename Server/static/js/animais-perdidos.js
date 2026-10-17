(() => {
    const form = document.getElementById("formAnimalPerdido");
    const alerta = document.getElementById("animal-alert");
    const lista = document.getElementById("animais-recentes");
    const inputImagem = document.getElementById("animal-imagem");
    const previewBox = document.getElementById("animal-preview-box");
    const preview = document.getElementById("animal-preview");
    const submit = document.getElementById("animal-submit");

    function esc(valor) {
        return String(valor ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
        }[c]));
    }

    function dataPt(data) {
        if (!data) return "Não informada";
        const [ano, mes, dia] = data.split("-");
        return (ano && mes && dia) ? `${dia}/${mes}/${ano}` : data;
    }

    function mostrarAlerta(texto, tipo = "success") {
        alerta.textContent = texto;
        alerta.className = `alert alert-${tipo}`;
        alerta.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function card(animal) {
        const imagem = animal.tem_imagem
            ? `<img class="animal-card-image" src="/api/animais-perdidos/${animal.id}/imagem"
                    alt="Foto de ${esc(animal.nome)}" loading="lazy">`
            : `<div class="animal-card-placeholder"><i class="bi bi-paw-fill"></i></div>`;

        const classeStatus = animal.status === "Encontrado"
            ? "animal-status-found"
            : "animal-status-lost";

        const acaoEncontrado = animal.pode_marcar_encontrado
            ? `<button type="button" class="btn btn-sm btn-outline-success mt-3 marcar-encontrado" data-animal-id="${animal.id}">
                    <i class="bi bi-check-circle me-1"></i> Marcar como encontrado
               </button>`
            : "";

        return `
            <div class="col-md-6 col-xl-4">
                <article class="animal-card">
                    ${imagem}
                    <div class="animal-card-body">
                        <div class="d-flex justify-content-between gap-2 align-items-start mb-2">
                            <h3>${esc(animal.nome)}</h3>
                            <span class="animal-status ${classeStatus}">${esc(animal.status)}</span>
                        </div>

                        <p class="animal-meta">
                            <i class="bi bi-geo-alt-fill"></i> ${esc(animal.local)}
                        </p>

                        <p class="animal-meta">
                            <strong>${esc(animal.especie)}</strong> · ${esc(animal.sexo)}
                        </p>

                        <p class="animal-description">${esc(animal.descricao)}</p>

                        <p class="animal-meta mb-1">
                            <i class="bi bi-calendar-event-fill"></i>
                            Visto em ${dataPt(animal.data_ocorrido)}
                        </p>

                        <div class="animal-contact">
                            <strong><i class="bi bi-telephone-fill me-1"></i> Contato</strong>
                            <div>${esc(animal.contato)}</div>
                        </div>
                        ${acaoEncontrado}
                    </div>
                </article>
            </div>
        `;
    }

    async function carregarRecentes() {
        try {
            const response = await fetch("/api/animais-perdidos?limit=6");
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || "Erro ao carregar.");
            }

            const animais = Array.isArray(result.data) ? result.data : [];

            if (!animais.length) {
                lista.innerHTML = `
                    <div class="col-12">
                        <div class="animal-empty">
                            <i class="bi bi-search-heart fs-1"></i>
                            <h3 class="h5 mt-3">Ainda não há publicações.</h3>
                            <p class="mb-0">Se souber de um animal perdido ou encontrado, faça o primeiro cadastro.</p>
                        </div>
                    </div>
                `;
                return;
            }

            lista.innerHTML = animais.map(card).join("");
        } catch (error) {
            lista.innerHTML = `
                <div class="col-12">
                    <div class="animal-empty">
                        <i class="bi bi-exclamation-circle fs-1 text-danger"></i>
                        <p class="mt-3 mb-0">Não foi possível carregar as publicações.</p>
                    </div>
                </div>
            `;
        }
    }

    inputImagem?.addEventListener("change", () => {
        const file = inputImagem.files?.[0];

        if (!file) {
            previewBox.classList.add("d-none");
            preview.removeAttribute("src");
            return;
        }

        if (!file.type.startsWith("image/")) {
            inputImagem.value = "";
            previewBox.classList.add("d-none");
            mostrarAlerta("Escolha um arquivo de imagem válido.", "danger");
            return;
        }

        preview.src = URL.createObjectURL(file);
        previewBox.classList.remove("d-none");
    });

    form?.addEventListener("reset", () => {
        setTimeout(() => {
            previewBox.classList.add("d-none");
            preview.removeAttribute("src");
        }, 0);
    });

    lista?.addEventListener("click", async (event) => {
        const button = event.target.closest(".marcar-encontrado");
        if (!button) return;
        button.disabled = true;
        try {
            const response = await fetch(`/api/animais-perdidos/${button.dataset.animalId}/status`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json", "Accept": "application/json" },
                body: JSON.stringify({ status: "Encontrado" })
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || "Não foi possível atualizar a publicação.");
            }
            mostrarAlerta(result.message || "Animal marcado como encontrado.", "success");
            await carregarRecentes();
        } catch (error) {
            mostrarAlerta(error.message || "Não foi possível atualizar a publicação.", "danger");
            button.disabled = false;
        }
    });

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();

        submit.disabled = true;
        submit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Publicando...';

        try {
            const formData = new FormData(form);

            const response = await fetch("/api/animais-perdidos", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                const detalhes = result.details && typeof result.details === "object"
                    ? Object.values(result.details).join(" ")
                    : "";
                throw new Error(
                    [result.error || result.message || "Não foi possível cadastrar.", detalhes]
                        .filter(Boolean)
                        .join(" ")
                );
            }

            mostrarAlerta(result.message || "Animal cadastrado com sucesso!", "success");
            form.reset();
            await carregarRecentes();
        } catch (error) {
            mostrarAlerta(
                error.message || "Erro de conexão com o servidor.",
                "danger"
            );
        } finally {
            submit.disabled = false;
            submit.innerHTML = '<i class="bi bi-send-fill me-1"></i> Publicar cadastro';
        }
    });

    carregarRecentes();
})();

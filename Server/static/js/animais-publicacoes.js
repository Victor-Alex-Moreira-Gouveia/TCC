(() => {
    const lista = document.getElementById("listaAnimais");
    const filtroTexto = document.getElementById("filtroTexto");
    const filtroStatus = document.getElementById("filtroStatus");
    const limpar = document.getElementById("limparFiltros");
    const contador = document.getElementById("contadorAnimais");

    let animais = [];

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

    function renderizar() {
        const termo = filtroTexto.value.trim().toLocaleLowerCase("pt-BR");
        const status = filtroStatus.value;

        const filtrados = animais.filter((animal) => {
            const texto = [
                animal.nome,
                animal.especie,
                animal.local,
                animal.descricao
            ].join(" ").toLocaleLowerCase("pt-BR");

            return texto.includes(termo)
                && (!status || animal.status === status);
        });

        contador.textContent = `${filtrados.length} ${filtrados.length === 1 ? "publicação" : "publicações"}`;

        if (!filtrados.length) {
            lista.innerHTML = `
                <div class="col-12">
                    <div class="animal-empty">
                        <i class="bi bi-search fs-1"></i>
                        <h3 class="h5 mt-3">Nenhuma publicação encontrada.</h3>
                        <p class="mb-0">Tente alterar sua pesquisa ou os filtros.</p>
                    </div>
                </div>
            `;
            return;
        }

        lista.innerHTML = filtrados.map((animal) => {
            const imagem = animal.tem_imagem
                ? `<img class="animal-card-image"
                        src="/api/animais-perdidos/${animal.id}/imagem"
                        alt="Foto de ${esc(animal.nome)}" loading="lazy">`
                : `<div class="animal-card-placeholder"><i class="bi bi-paw-fill"></i></div>`;

            const statusClass = animal.status === "Encontrado"
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
                                <span class="animal-status ${statusClass}">${esc(animal.status)}</span>
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
        }).join("");
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

    filtroTexto.addEventListener("input", renderizar);
    filtroStatus.addEventListener("change", renderizar);

    lista.addEventListener("click", async (event) => {
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
            await carregar();
        } catch (error) {
            window.alert(error.message || "Não foi possível atualizar a publicação.");
            button.disabled = false;
        }
    });

    limpar.addEventListener("click", () => {
        filtroTexto.value = "";
        filtroStatus.value = "";
        renderizar();
    });

    carregar();
})();

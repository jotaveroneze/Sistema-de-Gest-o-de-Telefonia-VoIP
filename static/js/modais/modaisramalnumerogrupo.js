async function visualizarRamalNumeroGrupo(idNumeroGrupo, numeroGrupoTexto) {
    try {
        numeroGrupoAtivoId = idNumeroGrupo;
        numeroGrupoAtivoTexto = numeroGrupoTexto;
        idNumeroGrupoAtual = idNumeroGrupo;
        const response = await fetch(`/ramalnumerogrupo/listar/${idNumeroGrupo}`);
        if (!response.ok) throw new Error("Erro ao buscar ramal");

        const dados = await response.json();

        renderTabelaRamalNumeroGrupo(dados.ramais);

        document.getElementById("labelNumeroGrupo").textContent =
            numeroGrupoTexto || dados.numerogrupo;

        const modalEl = document.getElementById("modalVisualizarRamalNumerogrupo");

        if (!modalVisualizarRamalNumeroGrupo) {
            modalVisualizarRamalNumeroGrupo =
                new bootstrap.Modal(modalEl);
        }

        if (!modalEl.classList.contains("show")) {
            modalVisualizarRamalNumeroGrupo.show();
        }

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar ramais do grupo");
    }
}

function renderTabelaRamalNumeroGrupo(lista) {
    const tbody = document.querySelector("#tabelaRamalNumeroGrupo tbody");
    tbody.innerHTML = "";

    lista.forEach((dep, index) => {
        const tr = document.createElement("tr");

        // Botão de subir, desabilitado para o primeiro item
        const upButton = `
            <button type="button"
                    class="btn btn-light btn-sm"
                    title="Subir na ordem"
                    onclick="alterarOrdemRamal(${dep.id}, 'subir')"
                    ${index === 0 ? 'disabled' : ''}>
                <i class="fa-solid fa-arrow-up"></i>
            </button>`;

        // Botão de descer, desabilitado para o último item
        const downButton = `
            <button type="button"
                    class="btn btn-light btn-sm"
                    title="Descer na ordem"
                    onclick="alterarOrdemRamal(${dep.id}, 'descer')"
                    ${index === lista.length - 1 ? 'disabled' : ''}>
                <i class="fa-solid fa-arrow-down"></i>
            </button>`;

        tr.innerHTML = `
            <td>${dep.ramal}</td>
            <td>${dep.ordem}</td>
            <td class="text-center">
                <div class="btn-group" role="group">
                    ${upButton}
                    ${downButton}
                </div>
                <button type="button"
                        class="btn btn-secondary btn-sm"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        title="Visualizar número de grupo do ramal"
                        onclick="abrirRamalApartirDoNumeroGrupo(${dep.idramal}, '${dep.ramal}')">
                <i class="fa-solid fa-phone-volume"></i>
                </button>
                <button type="button"
                        class="btn btn-outline-danger btn-sm"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        title="Desvincular ramal do número de grupo"
                        onclick="desvincularRamalNumeroGrupo(${dep.id})">
                    <i class="fa-solid fa-link-slash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    // Inicializa os tooltips do Bootstrap, se estiver usando
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

async function alterarOrdemRamal(idVinculo, direcao) {
    try {
        const response = await fetch(`ramalnumerogrupo/api/ramalnumerogrupo/${idVinculo}/alterar-ordem`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Incluir headers de autenticação, se necessário (ex: JWT)
                // 'Authorization': `Bearer ${seuToken}`
            },
            body: JSON.stringify({ direcao: direcao })
        });

        const result = await response.json();

        if (response.ok && result.success) {

            visualizarRamalNumeroGrupo(idNumeroGrupoAtual);
            // Recarregue a lista de ramais do grupo para atualizar a interface.
        } else {
            // Tratar erro
            console.error('Erro ao alterar a ordem:', result.erro || 'Erro desconhecido');
            alert('Erro ao alterar a ordem: ' + (result.erro || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        alert('Ocorreu um erro de comunicação com o servidor.');
    }
}

function abrirRamalApartirDoNumeroGrupo(idRamal, ramalTexto) {

    // 🔒 Fecha modal do Número de Grupo
    const modalGrupoEl = document.getElementById("modalVisualizarRamalNumerogrupo");
    const modalGrupo = bootstrap.Modal.getInstance(modalGrupoEl);

        fecharModaisVinculo();
    // ⏳ Aguarda a animação do Bootstrap
    setTimeout(() => {
        visualizarRamal(idRamal, ramalTexto);
    }, 300);
}


async function desvincularRamalNumeroGrupo(idRamalNumeroGrupo) {
    if (!confirm("Deseja realmente desvincular este ramal do número de grupo?")) {
        return;
    }

    try {
        const response = await fetch(
            `/ramalnumerogrupo/desvincular/${idRamalNumeroGrupo}`,
            { method: "DELETE" }
        );

        if (!response.ok) throw new Error("Erro ao desvincular");

        // 🔄 Atualiza SOMENTE a tabela
        const dados = await fetch(
            `/ramalnumerogrupo/listar/${numeroGrupoAtivoId}`
        ).then(r => r.json());

        renderTabelaRamalNumeroGrupo(dados.ramais);

    } catch (err) {
        console.error(err);
        alert("Erro ao desvincular ramal");
    }
}



function abrirModalAdicionarRamalNumeroGrupo() {
    if (!numeroGrupoAtivoId) {
        alert("Nenhum número de grupo selecionado");
        return;
    }

    // Label correta
    document.getElementById("labelNumeroGrupoAdicionar").textContent =
        numeroGrupoAtivoTexto;

    // ✅ PASSA O ID REAL DO GRUPO
    carregarRamaisDisponiveis(numeroGrupoAtivoId);

   abrirModal("modalAdicionarRamalNumeroGrupo")
}

async function carregarRamaisDisponiveis(idNumeroGrupo) {
    try {
        const response = await fetch(`/ramal/listar-disponiveis/${idNumeroGrupo}`);
        if (!response.ok) throw new Error("Erro ao buscar ramais");

        ramaisDisponiveis = await response.json();

        renderTabelaRamaisDisponiveis(ramaisDisponiveis);

        // limpa search
        document.getElementById("searchRamalAdicionar").value = "";

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar ramais disponíveis");
    }
}

function toggleRamalSelecionado(checkbox) {
    const id = parseInt(checkbox.value);

    if (checkbox.checked) {
        if (!ramaisSelecionados.includes(id)) {
            ramaisSelecionados.push(id);
        }
    } else {
        ramaisSelecionados = ramaisSelecionados.filter(r => r !== id);
    }

    console.log("Ramais selecionados:", ramaisSelecionados);
}

async function salvarRamalNumeroGrupo() {
    if (ramaisSelecionados.length === 0) {
        alert("Selecione ao menos um ramal");
        return;
    }

    try {
        const response = await fetch("/ramalnumerogrupo/adicionar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                idnumerogrupo: numeroGrupoAtivoId,
                ramais: ramaisSelecionados
            })
        });

        if (!response.ok) throw new Error("Erro ao salvar");

        // 🔄 Atualiza modal de visualização
        visualizarRamalNumeroGrupo(
            numeroGrupoAtivoId,
            numeroGrupoAtivoTexto
        );

    const modalEl = document.getElementById("modalAdicionarRamalNumeroGrupo");

    if (modalEl) {
        const modalInstance =
            bootstrap.Modal.getInstance(modalEl) ||
            new bootstrap.Modal(modalEl);

        modalInstance.hide();
    }
        ramaisSelecionados = [];

    } catch (err) {
        console.error(err);
        alert("Erro ao adicionar ramais");
    }
}

function renderTabelaRamaisDisponiveis(lista) {
    const tbody = document.querySelector(
        "#tabelaAdicionarRamalNumeroGrupo tbody"
    );
    tbody.innerHTML = "";

    lista.forEach(r => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="text-center">
                <input type="checkbox"
                       value="${r.id}"
                       onchange="toggleRamalSelecionado(this)"
                       ${ramaisSelecionados.includes(r.id) ? "checked" : ""}>
            </td>
            <td>${r.ramal}</td>
            <td class="text-center">
                <button class="btn btn-secondary btn-sm"
                        title="Visualizar número de grupo do ramal"
                        onclick="abrirRamalDoModalAdicionar(${r.id}, '${r.ramal}')">
                    <i class="fa-solid fa-phone-volume"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function fecharTodosOsModais() {
        fecharModaisVinculo();
}


function abrirRamalDoModalAdicionar(idRamal, ramalTexto) {

    // 🔒 Fecha TODOS os modais abertos
    fecharTodosOsModais();

    // ⏳ Aguarda animação do Bootstrap
    setTimeout(() => {
        visualizarRamal(idRamal, ramalTexto);
    }, 300);
}


document.getElementById("searchRamalAdicionar").addEventListener("input", function () {
    const texto = this.value.toLowerCase();

    const filtrados = ramaisDisponiveis.filter(r =>
        r.ramal.toString().includes(texto)
    );

    renderTabelaRamaisDisponiveis(filtrados);
});

document
    .getElementById("searchNumeroGrupoAdicionar")
    .addEventListener("input", function () {

        const texto = this.value.toLowerCase();

        const filtrados = numerosGrupoDisponiveis.filter(g =>
            g.numero.toString().toLowerCase().includes(texto)
        );

        renderTabelaNumerosGrupoDisponiveis(filtrados);
    });


async function visualizarRamal(idRamal, ramalTexto) {
    try {
        ramalAtivoId = idRamal;
        ramalAtivoTexto = ramalTexto;

        const response = await fetch(`/ramalnumerogrupo/listar-por-ramal/${idRamal}`);
        if (!response.ok) throw new Error("Erro ao buscar vínculos");

        const dados = await response.json();

        renderTabelaNumeroGrupoRamal(dados.grupos);

        document.getElementById("labelRamal").textContent =
            ramalTexto || dados.ramal;

        new bootstrap.Modal(
            document.getElementById("modalVisualizarRamal")
        ).show();

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar números de grupo");
    }
}

function renderTabelaNumeroGrupoRamal(lista) {
    const tbody = document.querySelector("#tabelaNumeroGrupoRamal tbody");
    tbody.innerHTML = "";

    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${item.numerogrupo}</td>

            <td class="text-center">

                <button class="btn btn-info btn-sm"
                        title="Visualizar ramais do número de grupo"
                        onclick="abrirNumeroGrupoApartirDoRamal(${item.idnumerogrupo}, '${item.numerogrupo}')">
                <i class="fa-solid fa-network-wired"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm"
                        onclick="desvincularNumeroGrupoDoRamal(${item.id})"
                        title="Desvincular número de grupo">
                    <i class="fa-solid fa-link-slash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function abrirNumeroGrupoApartirDoRamal(idNumeroGrupo, numeroGrupoTexto) {

    // 🔒 Fecha TODOS os modais abertos
    fecharTodosOsModais();

    // ⏳ Aguarda animação do Bootstrap
    setTimeout(() => {
        visualizarRamalNumeroGrupo(idNumeroGrupo, numeroGrupoTexto);
    }, 300);
}



function abrirModalAdicionarNumeroGrupoRamal() {
    if (!ramalAtivoId) {
        alert("Nenhum ramal selecionado");
        return;
    }

    // Label do ramal no modal
    document.getElementById("labelRamalAdicionar").textContent =
        ramalAtivoTexto;

    // Carrega números de grupo disponíveis para este ramal
    carregarNumerosGrupoDisponiveis(ramalAtivoId);

    abrirModal("modalAdicionarNumeroGrupoRamal")
}

async function carregarNumerosGrupoDisponiveis(idRamal) {
    try {
        const response = await fetch(
            `/ramalnumerogrupo/numerogrupo-disponiveis/${idRamal}`
        );

        if (!response.ok) throw new Error();

        numerosGrupoDisponiveis = await response.json();
        numerosGrupoSelecionados = [];

        renderTabelaNumerosGrupoDisponiveis(numerosGrupoDisponiveis);

        // limpa search
        document.getElementById("searchNumeroGrupoAdicionar").value = "";

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar números de grupo");
    }
}


function renderTabelaNumerosGrupoDisponiveis(lista) {
    const tbody = document.querySelector(
        "#tabelaAdicionarNumeroGrupoRamal tbody"
    );

    tbody.innerHTML = "";

    lista.forEach(g => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="text-center">
                <input type="checkbox"
                       value="${g.id}"
                       onchange="toggleNumeroGrupoSelecionado(this)">
            </td>
            <td>${g.numero}</td>
            <td class="text-center">
                <button class="btn btn-info btn-sm"
                        title="Visualizar ramais do número de grupo"
                        onclick="abrirNumeroGrupoDoModalAdicionar(${g.id}, '${g.numero}')">
                    <i class="fa-solid fa-network-wired"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function abrirNumeroGrupoDoModalAdicionar(idNumeroGrupo, numeroGrupoTexto) {

    // 🔒 Fecha TODOS os modais abertos
    fecharTodosOsModais();

    // ⏳ Aguarda animação do Bootstrap
    setTimeout(() => {
        visualizarRamalNumeroGrupo(idNumeroGrupo, numeroGrupoTexto);
    }, 300);
}



function toggleNumeroGrupoSelecionado(checkbox) {
    const id = parseInt(checkbox.value);

    if (checkbox.checked) {
        numerosGrupoSelecionados.push(id);
    } else {
        numerosGrupoSelecionados =
            numerosGrupoSelecionados.filter(n => n !== id);
    }
}


async function salvarNumeroGrupoRamal() {
    if (numerosGrupoSelecionados.length === 0) {
        alert("Selecione ao menos um número de grupo");
        return;
    }

    try {
        const response = await fetch("/ramalnumerogrupo/adicionar-por-ramal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idramal: ramalAtivoId,
                grupos: numerosGrupoSelecionados
            })
        });

        if (!response.ok) throw new Error();

        // 🔄 Atualiza modal de visualização
        visualizarRamal(ramalAtivoId, ramalAtivoTexto);

    const modalGrupoEl = document.getElementById("modalAdicionarNumeroGrupoRamal");

    if (!modalGrupoEl) return;

    const modalInstance =
        bootstrap.Modal.getInstance(modalGrupoEl) ||
        new bootstrap.Modal(modalGrupoEl);

    modalInstance.hide();

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar vínculos");
    }
}

async function desvincularNumeroGrupoDoRamal(idRamalNumeroGrupo) {
    if (!confirm("Deseja realmente desvincular este número de grupo do ramal?")) {
        return;
    }

    try {
        const response = await fetch(
            `/ramalnumerogrupo/desvincular-por-ramal/${idRamalNumeroGrupo}`,
            { method: "DELETE" }
        );

        if (!response.ok) throw new Error("Erro ao desvincular");

        // 🔄 Atualiza SOMENTE a tabela (sem abrir modal)
        const dados = await fetch(
            `/ramalnumerogrupo/listar-por-ramal/${ramalAtivoId}`
        ).then(r => r.json());

        renderTabelaNumeroGrupoRamal(dados.grupos);

    } catch (err) {
        console.error(err);
        alert("Erro ao desvincular número de grupo");
    }
}




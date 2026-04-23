// ===============================
// VARIÁVEIS GLOBAIS
// ===============================

// ===============================
// CARREGAR DO BACKEND
// ===============================
async function carregarGruposCaptura() {
    try {
        const response = await fetch('/grupocaptura/listar');
        if (!response.ok) throw new Error("Erro ao buscar grupos de captura");

        grupocapturas = await response.json();
        renderTabelaGrupoCaptura(grupocapturas);
        renderTabelaGrupoCapturaEditar(grupocapturas);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar grupos de captura");
    }
}


// ===============================
// RENDER TABELA PRINCIPAL
// ===============================
function renderTabelaGrupoCaptura(lista) {
    const tbody = document.querySelector("#tabelaGrupoCaptura tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    lista.forEach(grupo => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="grupoCapturaSelecionado"
                    value="${grupo.id}"
                    ${grupo.id === grupoCapturaSelecionadoId ? "checked" : ""}>
            </td>

            <td>${grupo.nome}</td>

            <td class="text-center" style="width: 120px;">
                <button type="button"
                    class="btn btn-warning btn-sm me-1"
                    title="Editar grupo de captura"
                    onclick="abrirEditarGrupoCaptura(${grupo.id})">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button type="button"
                    class="btn btn-danger btn-sm"
                    title="Excluir grupo de captura"
                    onclick="removerGrupoCaptura(${grupo.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    // Atualiza grupo selecionado
    tbody.querySelectorAll('input[name="grupoCapturaSelecionado"]').forEach(radio => {
        radio.addEventListener('change', function () {
            grupoCapturaSelecionadoId = parseInt(this.value);
            console.log("Grupo captura selecionado:", grupoCapturaSelecionadoId);
        });
    });
}


// ===============================
// REMOVER
// ===============================
async function removerGrupoCaptura(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este grupo de captura?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/grupocaptura/remover/${id}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        const dados = await resposta.json();

        if (resposta.ok) {
            alert(dados.mensagem);
            carregarGruposCaptura();
        } else {
            alert(dados.erro || "Erro ao remover grupo de captura");
        }

    } catch (e) {
        console.error(e);
        alert("Erro na requisição!");
    }
}


// ===============================
// EDITAR
// ===============================
function abrirEditarGrupoCaptura(id) {
    const grupo = grupocapturas.find(g => g.id === id);
    if (!grupo) return alert("Grupo de captura não encontrado!");

    document.getElementById("editarIdGrupoCaptura").value = grupo.id;
    document.getElementById("editarNome").value = grupo.nome;

    const modalEl = document.getElementById("modalEditarGrupoCaptura");
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
}



async function salvarEdicaoGrupoCaptura() {
    const id = document.getElementById("editarIdGrupoCaptura").value;
    const nome = document.getElementById("editarNome").value.trim();

    if (!nome) return alert("Preencha o nome!");

    try {
        const resp = await fetch(`/grupocaptura/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome })
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert("Erro: " + (erro.mensagem || erro.error));
        }

        alert("Grupo de captura atualizado com sucesso!");
        fecharModais();
        carregarGruposCaptura();

    } catch (e) {
        console.error(e);
        alert("Erro ao editar grupo de captura!");
    }
}


// ===============================
// MODAL ADICIONAR
// ===============================
function abrirAdicionarGrupoCaptura() {
    abrirModal("modalAdicionarGrupoCaptura");
}


// ===============================
// FILTRO MODAL EDITAR
// ===============================
function carregarGrupoCapturaEditar() {
    const pesquisa = document.getElementById("searchGrupoCapturaEditar").value.toLowerCase();

    const filtrados = grupocapturas.filter(g =>
        g.nome.toLowerCase().includes(pesquisa)
    );

    renderTabelaGrupoCapturaEditar(filtrados);
}

function renderTabelaGrupoCapturaEditar(lista) {
    const tbody = document.querySelector("#tabelaGrupoCapturaEditar tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    lista.forEach(grupo => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="grupoCapturaEdit"
                    value="${grupo.id}"
                    ${grupo.id === grupoCapturaSelecionadoEditarId ? "checked" : ""}>
            </td>

            <td>${grupo.nome}</td>

            <td class="text-center" style="width: 120px;">
                <button class="btn btn-warning btn-sm me-1"
                    onclick="abrirEditarGrupoCaptura(${grupo.id})">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    onclick="removerGrupoCaptura(${grupo.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('input[name="grupoCapturaEdit"]').forEach(radio => {
        radio.addEventListener("change", function () {
            grupoCapturaSelecionadoEditarId = parseInt(this.value);
            console.log("Grupo captura selecionado para EDITAR:", grupoCapturaSelecionadoEditarId);
        });
    });
}


// ===============================
// FILTROS INPUT
// ===============================
document.getElementById("searchGrupoCapturaEditar")?.addEventListener("input", carregarGrupoCapturaEditar);

document.getElementById("searchGrupoCaptura")?.addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    const linhas = document.querySelectorAll("#tabelaGrupoCaptura tbody tr");

    linhas.forEach(linha => {
        linha.style.display = linha.innerText.toLowerCase().includes(filtro) ? "" : "none";
    });
});


async function abrirEditarGrupoCapturaRamal(idRamal, numeroRamal, grupoAtual) {

    ramalSelecionadoId = idRamal;

    document.getElementById("ramalNumero").innerText = numeroRamal;
    document.getElementById("grupoAtual").innerText = grupoAtual || "—";

    grupoAtual = (grupoAtual || "").trim();

    const tbody = document.getElementById("tabelaGruposCaptura");
    tbody.innerHTML = "";

    try {
        const response = await fetch("/grupocaptura/listar");
        const grupos = await response.json();

        grupos.forEach(g => {
            const checked = g.nome === grupoAtual ? "checked" : "";

            tbody.innerHTML += `
                <tr>
                  <td class="text-center">
                    <input type="checkbox"
                        name="grupoCaptura"
                        value="${g.id}"
                        ${checked}
                        onclick="selecionarUnicoGrupo(this)">
                  </td>
                  <td>${g.nome}</td>
                </tr>
            `;
        });

        // 🔑 Abre o modal SOMENTE depois de montar tudo
         abrirModal("modalGrupoCaptura");

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar grupos de captura");
    }
}



function selecionarUnicoGrupo(checkbox) {
    document
        .querySelectorAll("input[name='grupoCaptura']")
        .forEach(cb => {
            if (cb !== checkbox) cb.checked = false;
        });
}


//#region ADICIONAR
//#region ADICIONAR
window.salvarGrupoCaptura = async function () {
    const nomeInput = document.getElementById("addNome");
    if (!nomeInput) {
        alert("Campo nome não encontrado");
        return;
    }

    const nome = nomeInput.value.trim();
    if (!nome) {
        alert("Preencha o nome!");
        return;
    }

    try {
        const resp = await fetch("/grupocaptura/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome })
        });

        const resultado = await resp.json();  // ✅ Lê ANTES das verificações

        console.log("Status:", resp.status, "Resultado:", resultado[1]);  // 🔍 Debug

        // ✅ Verifica 409 PRIMEIRO
        if (resultado[1] === 409) {
            alert("Esse grupo de captura já existe!");
            return;
        }

        if (!resp.ok) {
            alert("Erro ao cadastrar: " + (resultado.erro || "Erro desconhecido"));
            return;
        }

        // ✅ Só executa se foi 201
        nomeInput.value = "";
        alert("Grupo de captura cadastrado com sucesso!");
        window.location.href = "/grupocaptura";

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar grupo de captura");
    }
};



async function abrirVisualizarGrupoCaptura(idGrupo, nomeGrupo) {

    document.getElementById("nomeGrupoCaptura").innerText = nomeGrupo;
    document.getElementById("idGrupoCapturaSelecionado").value = idGrupo;

    const tbody = document.getElementById("tbodyRamaisGrupoCaptura");
    tbody.innerHTML = `
        <tr>
            <td colspan="3" class="text-center text-muted">Carregando...</td>
        </tr>
    `;

    const modalElement = document.getElementById("modalVisualizarGrupoCaptura");

    if (!modalVisualizarGrupoCapturaInstance) {
        modalVisualizarGrupoCapturaInstance = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
    }

    modalVisualizarGrupoCapturaInstance.show();

    try {
        const response = await fetch(`/grupocaptura/ramais/${idGrupo}`);
        const ramais = await response.json();

        if (!ramais.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-muted">
                        Nenhum ramal vinculado
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = "";

        ramais.forEach(r => {
            tbody.innerHTML += `
                <tr>
                    <td>${r.numero}</td>
                    <td>${r.usuarios?.length ? r.usuarios.join("<br>") : "-"}</td>
                    <td class="text-center">
                        <button class="btn btn-danger btn-sm"
                                title="Desvincular ramal"
                                onclick="desvincularRamalGrupoCaptura(${r.id})">
                            <i class="fa-solid fa-unlink"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-danger">
                    Erro ao carregar ramais
                </td>
            </tr>
        `;
    }
}



async function desvincularRamalGrupoCaptura(idRamal) {

    if (!confirm("Deseja realmente desvincular este ramal do grupo de captura?")) {
        return;
    }

    const idGrupo = document.getElementById("idGrupoCapturaSelecionado").value;

    try {
        const response = await fetch("/grupocaptura/desvincular-ramal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idramal: idRamal })
        });

        if (!response.ok) {
            throw new Error();
        }

        // 🔄 Reabre o modal já atualizado
        abrirVisualizarGrupoCaptura(
            idGrupo,
            document.getElementById("nomeGrupoCaptura").innerText
        );

    } catch (err) {
        alert("Erro ao desvincular ramal");
    }
}


async function abrirModalVincularRamal() {
    const idGrupo = document.getElementById("idGrupoCapturaSelecionado").value;
    const select = document.getElementById("selectRamalGrupoCaptura");

    select.innerHTML = `<option>Carregando...</option>`;

    const modal = new bootstrap.Modal(
        document.getElementById("modalVincularRamalGrupoCaptura")
    );
    modal.show();

    try {
        const response = await fetch("/ramal/disponiveis");

        if (!response.ok) throw new Error("Erro ao buscar ramais"); // ✅ verifica ok

        const ramais = await response.json();

        select.innerHTML = `<option value="">Selecione um ramal</option>`;
        ramais.forEach(r => {
            const option = document.createElement("option"); // ✅ evita XSS com innerHTML +=
            option.value = r.id;
            option.textContent = r.numero;
            select.appendChild(option);
        });

    } catch (err) {
        console.error(err); // ✅ loga o erro real
        select.innerHTML = `<option>Erro ao carregar ramais</option>`;
    }
}

async function vincularRamalGrupoCaptura() {
    const idGrupo = document.getElementById("idGrupoCapturaSelecionado").value;
    const idRamal = document.getElementById("selectRamalGrupoCaptura").value;

    // ✅ valida ambos
    if (!idGrupo) {
        alert("Grupo de captura não identificado");
        return;
    }
    if (!idRamal) {
        alert("Selecione um ramal");
        return;
    }

    try {
        const response = await fetch("/grupocaptura/vincular-ramal", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idgrupocaptura: parseInt(idGrupo, 10), // ✅ converte para inteiro
                idramal: parseInt(idRamal, 10)         // ✅ converte para inteiro
            })
        });

        if (response.ok) {
            bootstrap.Modal.getInstance(
                document.getElementById("modalVincularRamalGrupoCaptura")
            ).hide();

            abrirVisualizarGrupoCaptura(
                idGrupo,
                document.getElementById("nomeGrupoCaptura").innerText
            );
        } else {
            const erro = await response.text(); // ✅ captura mensagem real do servidor
            console.error("Erro do servidor:", erro);
            alert("Erro ao vincular ramal");
        }

    } catch (err) { // ✅ trata erros de rede
        console.error(err);
        alert("Erro de conexão ao vincular ramal");
    }
}



// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", carregarGruposCaptura);
// ================== NUMERO DE GRUPO- EDITAR ==================


function abrirEditarNumeroGrupo(id) {
    const ng = numeroGrupos.find(n => n.id === id);
    if (!ng) {
        alert("Número de Grupo não encontrado!");
        return;
    }

    // Preenche campos
    document.getElementById("editIdNumeroGrupo").value = ng.id;
    document.getElementById("editNumeroGrupo").value = ng.numero;
    document.getElementById("editDescricaoNumeroGrupo").value = ng.descricao ?? "";
    document.getElementById("editGravadoNumeroGrupo").value = ng.gravado;
    numeroGrupoSelecionadoEditarId = ng.id;

    carregarNumeroGrupoEditar(); // se existir, senão pode remover

    // Abre o modal
    abrirModal("modalEditarNumeroGrupo");
}



// Salvar edição
async function salvarEdicaoNumeroGrupo() {
    const id = document.getElementById("editIdNumeroGrupo").value;
    const numero = document.getElementById("editNumeroGrupo").value.trim();
    const descricao = document.getElementById("editDescricaoNumeroGrupo").value.trim();
    const gravado = document.getElementById("editGravadoNumeroGrupo").checked;
    const iddepartamento = departamentoSelecionadoEditarId || null;

    try {
        const resp = await fetch(`/numerogrupo/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ numero, descricao, gravado, iddepartamento })
        });

        const resultado = await resp.json();
        if (!resp.ok) {
            return alert("Erro: " + (resultado.erro || resultado.mensagem));
        }

        alert("Número de Grupo atualizado com sucesso!");
        fecharModais();
        carregarNumeroGrupo();
    } catch (e) {
        console.error(e);
        alert("Erro ao editar número de grupo!");
    }
}




function renderTabelaNumeroGrupoEditar(lista) {
    const tbody = document.querySelector("#tabelaNumeroGrupoEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(ng => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio"
                       name="numeroGrupoEdit"
                       value="${ng.id}"
                       ${ng.id === numeroGrupoSelecionadoEditarId ? "checked" : ""}>
            </td>

            <td>${ng.numero}</td>
            <td>${ng.descricao ?? ""}</td>

            <td class="text-center" style="width: 120px;">
                <button class="btn btn-warning btn-sm me-1"
                        title="Editar número de grupo"
                        onclick="abrirEditarNumeroGrupo(${ng.id})">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                        title="Excluir número de grupo"
                        onclick="removerNumeroGrupo(${ng.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });

    // Atualiza seleção
    tbody.querySelectorAll('input[name="numeroGrupoEdit"]').forEach(radio => {
        radio.addEventListener("change", function () {
            numeroGrupoSelecionadoEditarId = parseInt(this.value);
            console.log(
                "Número de Grupo selecionado para EDITAR:",
                numeroGrupoSelecionadoEditarId
            );
        });
    });
}



// Filtro de pesquisa
// Filtro de pesquisa
document
    .getElementById("searchNumeroGrupoEditar")
    .addEventListener("input", function () {
        const filtro = this.value.toLowerCase();
        const linhas = document.querySelectorAll(
            "#tabelaNumeroGrupoEditar tbody tr"
        );

        linhas.forEach(linha => {
            linha.style.display = linha.innerText.toLowerCase().includes(filtro)
                ? ""
                : "none";
        });
    });


function carregarNumeroGrupoEditar() {

    if (!numeroGrupos || numeroGrupos.length === 0) {
        console.warn("Números de Grupo ainda não carregados, tentando novamente...");
        carregarNumeroGrupo().then(() => carregarNumeroGrupoEditar());
        return;
    }

    const pesquisa = document
        .getElementById("searchNumeroGrupoEditar")
        .value
        .toLowerCase();

    const filtradas = numeroGrupos.filter(ng =>
        ng.numero.toLowerCase().includes(pesquisa) ||
        (ng.descricao ?? "").toLowerCase().includes(pesquisa)
    );

    renderTabelaNumeroGrupoEditar(filtradas);
}


// Inicializa
carregarNumeroGrupoEditar();

//#region DOM READY
document.addEventListener("DOMContentLoaded", () => {
    carregarGrupocapturas();

    const search = document.getElementById("searchGrupoCaptura");
    if (search) {
        search.addEventListener("input", function () {
            const filtro = this.value.toLowerCase();
            const filtrados = grupocapturas.filter(g =>
                g.nome.toLowerCase().includes(filtro)
            );
            preencherTabelaGrupocapturas(filtrados);
        });
    }
});
//#endregion


//#region LISTAGEM
async function carregarGrupocapturas() {
    mostrarLoadingTabela();
    try {
        const response = await fetch("/grupocaptura/listar");
        if (!response.ok) throw new Error("Erro ao buscar grupocapturas");

        grupocapturas = await response.json();
        preencherTabelaGrupocapturas(grupocapturas);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar grupos de captura");
    } finally {
        esconderLoadingTabela();
    }
}

function preencherTabelaGrupocapturas(lista) {
    const tabela = document.getElementById("tabelaGrupoCaptura");
    if (!tabela) {
        console.error("tabelaGrupoCaptura não encontrada");
        return;
    }

    tabela.innerHTML = "";

    lista.forEach(g => {
        tabela.innerHTML += `
            <tr>
                <td>${g.nome}</td>

                <td class="text-center">

            <button class="btn btn-info btn-sm"
                title="Visualizar grupo captura"
                onclick="abrirVisualizarGrupoCaptura(${g.id}, '${g.nome.replace(/'/g, "\\'")}')">
                <i class="fa-solid fa-eye"></i>
            </button>
                <button class="btn btn-warning btn-sm"
                        title="Editar grupo captura"
                        onclick="abrirEditarGrupoCaptura(${g.id}, '${g.nome.replace(/'/g, "\\'")}')">
                    <i class="fa-solid fa-pen"></i>
                </button>

                    <button class="btn btn-danger btn-sm"
                        title="Excluir grupo captura"
                        onclick="removerGrupocaptura(${g.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}
//#endregion


//#endregion


//#region EDITAR
window.abrirEditarGrupoCaptura = function (id, nome) {
    const idInput = document.getElementById("editarIdGrupoCaptura");
    const nomeInput = document.getElementById("editarNome");

    if (!idInput || !nomeInput) {
        alert("Erro ao abrir modal de edição");
        return;
    }

    idInput.value = id;
    nomeInput.value = nome;

    new bootstrap.Modal(
        document.getElementById("modalEditarGrupoCaptura")
    ).show();
};

window.salvarEdicaoGrupoCaptura = async function () {
    const idInput = document.getElementById("editarIdGrupoCaptura");
    const nomeInput = document.getElementById("editarNome");

    if (!idInput || !nomeInput) {
        alert("Erro ao carregar dados do modal");
        return;
    }

    const id = idInput.value;
    const nome = nomeInput.value.trim();

    if (!nome) {
        alert("Preencha o nome!");
        return;
    }

    try {
        const resp = await fetch(`/grupocaptura/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome })
        });

        if (!resp.ok) throw new Error("Erro ao editar");

        alert("Grupo de captura atualizado com sucesso!");
        window.location.href = '/grupocaptura';
        carregarGrupocapturas();
    } catch (e) {
        console.error(e);
        alert("Erro ao editar grupo de captura");
    }
};

async function removerGrupocaptura(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este grupo de captura?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/grupocaptura/remover/${id}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            return alert(dados.erro || "Erro ao remover grupo de captura");
        }

        alert(dados.mensagem || "Grupo de captura removido com sucesso!");

        // Recarrega lista
        if (typeof carregarGrupocapturas === "function") {
            carregarGrupocapturas();
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro ao remover grupo de captura");
    }
}

document.getElementById("searchGrupoCaptura")?.addEventListener("input", function () {
    const filtro = this.value.toLowerCase();

    const filtrados = grupocapturas.filter(gc =>
        gc.nome.toLowerCase().includes(filtro)
    );

    preencherTabelaGrupocapturas(filtrados);
});



//#endregion

//#region windows
document.addEventListener("DOMContentLoaded", () => {
    carregarEmpresa();
});

// Carregar windowss do banco
async function carregarEmpresa() {
    mostrarLoadingTabela();
    try {
        const response = await fetch('/empresa/listar');
        if (!response.ok) throw new Error("Erro ao buscar empresas");
        empresas = await response.json(); // preenche o array global
        preencherTabelaEmpresas(empresas);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar empresas");
    }
    finally {
        esconderLoadingTabela();
    }
    }

function preencherTabelaEmpresas(lista) {

    const tabela = document.getElementById("tabelaEmpresa");
    tabela.innerHTML = "";

    lista.forEach(sis => {
        tabela.innerHTML += `
            <tr>
                <td>${sis.nome}</td>
                <td>
                <button class="btn btn-warning btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Editar empresa"
                    onclick="abrirEditarEmpresa(${sis.id}, '${sis.nome}')">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir empresa"
                    onclick="removerEmpresa(${sis.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
                </td>
            </tr>
        `;
    });
}

// Filtrar departamentos ao digitar
document.getElementById("searchEmpresa").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = empresas.filter(d => d.nome.toLowerCase().includes(filtro));
    preencherTabelaEmpresas(filtrados); // renderiza apenas os filtrados
});


async function salvarEdicaoEmpresa() {

    const id = document.getElementById("editIdEmpresa").value;
    const nome = document.getElementById("editNomeEmpresa").value.trim();

    if (!nome) {
        alert("O nome da empresa é obrigatório!");
        return;
    }

    const dados = { nome };

    try {
        const resp = await fetch(`/empresa/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert("Erro: " + (erro.mensagem || erro.error));
        }

        alert("Empresa atualizada com sucesso!");

        window.location.href = '/empresa';
        // Atualiza tabela
        carregarEmpresas();

    } catch (e) {
        console.error(e);
        alert("Erro ao editar empresa!");
    }
}

function abrirEditarEmpresa(id, nome) {

    empresaSelecionadoEditarId = id;

    // Preenche campos do modal
    document.getElementById("editIdEmpresa").value = id;
    document.getElementById("editNomeEmpresa").value = nome;

    // Abre o modal
    new bootstrap.Modal(
        document.getElementById("modalEditarEmpresa")
    ).show();
}


//#endregion

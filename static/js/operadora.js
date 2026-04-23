//#region windows
document.addEventListener("DOMContentLoaded", () => {
    carregarOperadoras();
});

// Carregar windowss do banco
async function carregarOperadoras() {
    mostrarLoadingTabela();
    try {
        const response = await fetch('/operadora/listar');
        if (!response.ok) throw new Error("Erro ao buscar operadora");
        operadoras = await response.json();
        preencherTabelaOperadora(operadoras);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar operadora");
    }
    finally {
        esconderLoadingTabela();
    }
    }

function preencherTabelaOperadora(lista) {

    const tabela = document.getElementById("tabelaOperadora");
    tabela.innerHTML = "";

    lista.forEach(sis => {
        tabela.innerHTML += `
            <tr>
                <td>${sis.nome}</td>
                <td>${sis.contrato}</td>
                <td>${sis.processo}</td>
                <td>
                <button class="btn btn-warning btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Editar empresa"
                    onclick="abrirEditarOperadora(${sis.id}, '${sis.nome}', '${sis.contrato}', '${sis.processo}')">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir empresa"
                    onclick="removerOperadora(${sis.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
                </td>
            </tr>
        `;
    });
}


// Filtrar operadora ao digitar
document.getElementById("searchOperadora").addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    const filtrados = operadoras.filter(o =>
        o.nome.toLowerCase().includes(filtro)
    );
    preencherTabelaOperadora(filtrados);
});


//#region windows

// Carregar windowss do banco
async function carregarModelo() {
    try {
        const response = await fetch('/modelo/listar');
        if (!response.ok) throw new Error("Erro ao buscar modelos");
        modelos = await response.json(); // preenche o array global
        preencherTabelaModelos(modelos)
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar modelos");
    }
}


function preencherTabelaModelos(lista) {
    const tabela = document.getElementById("tabelaModelo");
    tabela.innerHTML = "";

    lista.forEach(sis => {
        tabela.innerHTML += `
            <tr>
                <td>${sis.nome}</td>
                <td>
                <button class="btn btn-warning btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Editar modelo"
                    onclick="abrirEditarModelo(${sis.id}, '${sis.nome}')">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir modelo"
                    onclick="removerModelo(${sis.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
                </td>
            </tr>
        `;
    });
}

document.getElementById("searchTelaModelo").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = modelos.filter(d => d.nome.toLowerCase().includes(filtro));
    preencherTabelaModelos(filtrados); // renderiza apenas os filtrados
});


document.addEventListener("DOMContentLoaded", function() {
    carregarModelo();
});
//#endregion

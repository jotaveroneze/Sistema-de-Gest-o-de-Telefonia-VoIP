//#region tronco


async function carregarTronco() {

    mostrarLoadingTabela();
    try {
        const response = await fetch('/tronco/listar');
        if (!response.ok) throw new Error("Erro ao buscar troncos");

        troncos = await response.json();
        preencherTabelaTroncos(troncos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar troncos");
    }
    finally {
        esconderLoadingTabela();
    }
}

function preencherTabelaTroncos(lista) {
    const tabela = document.getElementById("tabelaTronco");
    tabela.innerHTML = "";

    lista.forEach(dep => {
        tabela.innerHTML += `
            <tr id="tronco-${dep.id}">
                <td>${dep.numerochave}</td>
                <td>${dep.ramalinicial}</td>
                <td>${dep.ramalfinal}</td>
                <td>${dep.operadora}</td>
                <td>
                    <button class="btn btn-warning btn-sm"
                        title="Editar tronco"
                        onclick="abrirEditarTronco(${dep.id})">
                        <i class="fa-solid fa-pen"></i>
                    </button>

                    <button class="btn btn-danger btn-sm"
                        title="Excluir tronco"
                        onclick="removerTronco(${dep.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}


// Filtrar troncos ao digitar
document.getElementById("searchTronco").addEventListener("input", function () {
    const filtro = this.value.toLowerCase();

    const filtrados = troncos.filter(t =>
        (t.numerochave && t.numerochave.toLowerCase().includes(filtro)) ||
        (t.ramalinicial && t.ramalinicial.toString().includes(filtro)) ||
        (t.ramalfinal && t.ramalfinal.toString().includes(filtro))
    );

    preencherTabelaTroncos(filtrados);
});



// Função para salvar edição
async function salvarEdicaoTronco() {
    const id = document.getElementById("editIdTronco").value; // ✅ era "editId"

    const numerochave = document.getElementById("txtEditNumerochave").value.trim();
    const ramalinicial = document.getElementById("txtEditRamalinicial").value.trim();
    const ramalfinal = document.getElementById("txtEditRamalfinal").value.trim();

    if (!operadoraSelecionadaEditarId)
        return alert("Selecione uma operadora!");

    try {
        const resp = await fetch(`/tronco/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numerochave,
                ramalinicial,
                ramalfinal,
                idoperadora: operadoraSelecionadaEditarId
            })
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert(erro.mensagem || erro.error);
        }

        // ✅ Fecha modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(
            document.getElementById("modalEditarTronco")
        );
        if (modal) modal.hide();

        alert("Tronco atualizado com sucesso!");
        window.location.href = '/tronco'; // ✅ Remove carregarTronco() que nunca executaria

    } catch (e) {
        console.error(e);
        alert("Erro ao editar tronco");
    }
}



function abrirEditarTronco(id) {
    const dep = troncos.find(t => t.id === id);
    if (!dep) return alert("Tronco não encontrado!");

    document.getElementById("editIdTronco").value = dep.id;
    document.getElementById("txtEditNumerochave").value = dep.numerochave;
    document.getElementById("txtEditRamalinicial").value = dep.ramalinicial;
    document.getElementById("txtEditRamalfinal").value = dep.ramalfinal;

    operadoraSelecionadaEditarId = dep.idoperadora;

    carregarOperadorasEditar();

    new bootstrap.Modal(
        document.getElementById("modalEditarTronco")
    ).show();
}


document.addEventListener("DOMContentLoaded", () => {
    carregarTronco();
    carregarOperadorasEditar();
    carregarOperadoras();
});
//#endregion

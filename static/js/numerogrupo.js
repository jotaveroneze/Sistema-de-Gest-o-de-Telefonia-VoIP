//#region windows

// Carregar windowss do banco
async function carregarNumeroGrupo() {
    mostrarLoadingTabela();
    try {
        const response = await fetch('/numerogrupo/listar');
        if (!response.ok) throw new Error("Erro ao buscar numeros virtuais");
        numerosgrupo = await response.json(); // preenche o array global
        preencherTabelaNumeroGrupo(numerosgrupo)
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar numeros de grupo");
    }
    finally {
        esconderLoadingTabela();
    }
}

// Remover departamento do backend

function preencherTabelaNumeroGrupo(lista) {
    const tabela = document.getElementById("tabelaNumeroGrupo");
    tabela.innerHTML = "";

    lista.forEach(sis => {
        tabela.innerHTML += `
            <tr>
                <td>${sis.numero}</td>
                <td>${sis.numerochave}</td>
                <td>${sis.sigla}</td>
                <td>${sis.departamento}</td>
                <td>${sis.descricao || ''}</td>
                <td class="">
                ${sis.gravado
                    ? `<i class="fa-solid fa-microphone text-success" title="Gravação habilitada"></i>`
                    : `<i class="fa-solid fa-microphone-slash text-danger" title="Gravação desabilitada"></i>`
                }
                </td>
                <td class="text-center">
            <button class="btn btn-secondary btn-sm "
                data-bs-toggle="tooltip"
                title="Visualizar ramais do número virtual"
                onclick="visualizarRamalNumeroGrupo(${sis.id}, '${sis.numero}')">
                <i class="fa-solid fa-network-wired"></i>
            </button>

            <button class="btn btn-warning btn-sm"
                data-bs-toggle="tooltip"
                data-bs-placement="top"
                title="Editar número virtual"
                data-id="${sis.id}"
                data-numero="${sis.numero}"
                data-descricao="${sis.descricao ?? ''}"
                data-gravado="${sis.gravado}"
                onclick="abrirEditarNumeroGrupo(this)">
                <i class="fa-solid fa-pen"></i>
            </button>
                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir número virtual"
                    onclick="removerNumeroGrupo(${sis.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>

                </td>
            </tr>
        `;
    });
}


document.getElementById("searchNumeroGrupo").addEventListener("input", aplicarFiltrosNumeroGrupo);
document.getElementById("filtroGravadoNumeroGrupo").addEventListener("change", aplicarFiltrosNumeroGrupo);

function aplicarFiltrosNumeroGrupo() {
    const texto = document.getElementById("searchNumeroGrupo").value.toLowerCase();
    const gravadoFiltro = document.getElementById("filtroGravadoNumeroGrupo").value;

    const filtrar = (lista) => {
        return lista.filter(n => {
            // Busca em várias colunas
            const matchTexto =
                String(n.numero).toLowerCase().includes(texto) ||
                (n.departamento && n.departamento.toLowerCase().includes(texto)) ||
                (n.sigla && n.sigla.toLowerCase().includes(texto)) ||
                (n.descricao && n.descricao.toLowerCase().includes(texto));

            // Filtra gravado
            let matchGravado = true;
            if (gravadoFiltro === "gravado")
                matchGravado = n.gravado === 1 || n.gravado === true;
            if (gravadoFiltro === "nao_gravado")
                matchGravado = n.gravado === 0 || n.gravado === false;

            return matchTexto && matchGravado;
        });
    };

    preencherTabelaNumeroGrupo(filtrar(numerosgrupo));
}




// Função para abrir modal de edição via data-attributes
function abrirEditarNumeroGrupo(button) {
    const id = button.dataset.id;
    const numero = button.dataset.numero;
    const descricao = button.dataset.descricao;
    const gravado = button.dataset.gravado;

    // Preenche os campos do modal
    document.getElementById("editIdNumeroGrupo").value = id;
    document.getElementById("editNumeroGrupo").value = numero;
    document.getElementById("editDescricaoNumeroGrupo").value = descricao;
    document.getElementById("editGravadoNumeroGrupo").checked = gravado === "true" || gravado === "1";

    // Abre o modal
    const modalEl = document.getElementById('modalEditarNumeroGrupo');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
}



// Função para salvar edição
async function salvarEdicaoNumeroGrupo() {
    const id = document.getElementById("editIdNumeroGrupo").value;
    const numero = document.getElementById("editNumeroGrupo").value.trim();
    const descricao = document.getElementById("editDescricaoNumeroGrupo").value.trim();
    const gravado = document.getElementById("editGravadoNumeroGrupo").checked;
    const iddepartamento = departamentoSelecionadoEditarId;
    const idtronco = troncoSelecionadoId;

    if (!numero) return alert("O número virtual é obrigatório!");
    if (!idtronco) return alert("Selecione um tronco!");

    try {
        const resposta = await fetch(`/numerogrupo/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ numero, descricao, gravado, iddepartamento, idtronco })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            return alert("Erro ao atualizar número virtual: " + (resultado.erro || resultado.mensagem));
        }

        // ✅ Fecha modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(
            document.getElementById("modalEditarNumeroGrupo")
        );
        if (modal) modal.hide();

        alert("Número virtual atualizado com sucesso!");
        window.location.href = '/numerogrupo'; // ✅ Remove carregarNumeroGrupo() que nunca executaria

    } catch (erro) {
        console.error("Erro ao editar número virtual:", erro);
        alert("Erro ao editar número virtual");
    }
}


document.addEventListener("DOMContentLoaded", function() {
    carregarDepartamentos();
    carregarTroncoModal();
    carregarNumeroGrupo();
    carregarOperadoras();
    carregarTroncoEditar();
});
//#endregion

//#region windows
document.addEventListener("DOMContentLoaded", () => {
    carregarSecretarias();
});

// Carregar windowss do banco
async function carregarSecretarias() {
    mostrarLoadingTabela();
    try {
        const response = await fetch('/secretaria/listar');
        if (!response.ok) throw new Error("Erro ao buscar secretarias");
        secretarias = await response.json(); // preenche o array global
        preencherTabelaSecretarias(secretarias);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar secretarias");
    }
    finally {
        esconderLoadingTabela();
    }
    }

function preencherTabelaSecretarias(lista) {

    const tabela = document.getElementById("tabelaSecretaria");
    tabela.innerHTML = "";

    lista.forEach(sis => {
        tabela.innerHTML += `
            <tr>
                <td>${sis.sigla}</td>
                <td>${sis.nome}</td>
                <td>
                <button class="btn btn-warning btn-sm"
                        data-bs-toggle="tooltip"
                        data-bs-placement="top"
                        title="Editar secretaria"
                        onclick="abrirEditarSecretaria(${sis.id}, '${sis.sigla.replace(/'/g,"\\'")}', '${sis.nome.replace(/'/g,"\\'")}')">
                    <i class="fa-solid fa-pen"></i>
                </button>


                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir secretaria"
                    onclick="removerSecretaria(${sis.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
                </td>
            </tr>
        `;
    });
}

// Filtrar departamentos ao digitar
document.getElementById("searchSecretaria").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = secretarias.filter(d => d.nome.toLowerCase().includes(filtro));
    preencherTabelaSecretarias(filtrados); // renderiza apenas os filtrados
});


async function salvarEdicaoSecretaria() {
    const idInput = document.getElementById("editarIdSecretaria");
    const siglaInput = document.getElementById("editarSigla");
    const nomeInput = document.getElementById("editarNome");

    if (!idInput || !siglaInput || !nomeInput) {
        console.error("Inputs do modal não encontrados!");
        return alert("Erro: modal de edição não carregado corretamente.");
    }

    const id = idInput.value;
    const sigla = siglaInput.value.trim();
    const nome = nomeInput.value.trim();

    if (!sigla || !nome) {
        return alert("Preencha todos os campos!");
    }

    const dados = { sigla, nome };

    try {
        const resp = await fetch(`/secretaria/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert("Erro: " + (erro.mensagem || erro.error));
        }

        // ✅ Fecha o modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(
            document.getElementById("modalEditarSecretaria")
        );
        if (modal) modal.hide();

        alert("Secretaria atualizada com sucesso!");
        window.location.href = '/secretaria'; // ✅ Barra no início, sem barra no final

    } catch (e) {
        console.error(e);
        alert("Erro ao editar secretaria!");
    }
}


function abrirEditarSecretaria(id, sigla, nome) {
    secretariaSelecionadoEditarId = id;

    // Preenche campos do modal
    document.getElementById("editarIdSecretaria").value = id;
    document.getElementById("editarSigla").value = sigla;
    document.getElementById("editarNome").value = nome;

    // Abre o modal
    new bootstrap.Modal(
        document.getElementById("modalEditarSecretaria")
    ).show();
}



//#endregion

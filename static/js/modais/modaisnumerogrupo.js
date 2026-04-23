// ================================ numerogrupo ================================================

async function carregarNumerogrupo() {
    try {
        const response = await fetch("/numerogrupo/listar");
        if (!response.ok) throw new Error("Erro ao buscar numero de grupo");

        numerosgrupo = await response.json();
        preencherTabelaNumeroGrupo(numerosgrupo);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar numero de grupo");
    }
}

function preencherTabelaNumeroGrupo(lista) {
    const tbody = document.querySelector("#tabelaNumeroGrupo tbody");
    tbody.innerHTML = "";

    lista.forEach(e => {
        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                    <input type="radio"
                           name="numerogrupo_add"
                           value="${e.id}"
                           onclick="selecionarNumeroGrupo(${e.id})">
                </td>

                <td>${e.numero}</td>
                <td>${e.numerochave}</td>
                <td>${e.departamento}</td>
                <td>${e.descricao ?? ""}</td>

                <td class="text-center" style="width: 120px;">
                    <button type="button"
                            class="btn btn-warning btn-sm me-1"
                            title="Editar número de grupo"
                            onclick="abrirEditarNumeroGrupo(${e.id}, '${e.numero}', '${e.descricao ?? ""}')">
                        <i class="fa-solid fa-pen"></i>
                    </button>

                    <button type="button"
                            class="btn btn-danger btn-sm"
                            title="Excluir número de grupo"
                            onclick="removerNumeroGrupo(${e.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}



function selecionarNumerogrupo(id) {
    numerogrupoSelecionadoId = id;
    console.log("Numero de grupo selecionada:", id);
}


function abrirAdicionarNumeroGrupo() {

    // Limpa campos do formulário
    const inputNumero = document.getElementById("txtAddNumeroGrupo");
    const inputDescricao = document.getElementById("txtAddDescricaoNumeroGrupo");

    if (inputNumero) inputNumero.value = "";
    if (inputDescricao) inputDescricao.value = "";

    // Reseta seleção
    numerogrupoSelecionadoId = null;



    // Abre o modal de adicionar
    abrirModal("modalAdicionarNumeroGrupo");
}


async function removerNumeroGrupo(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este Numero de Grupo?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/numerogrupo/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);
            carregarNumerogrupo()

            // Remove a linha da tabela
            const linha = document.getElementById(`numerogrupo-${id}`);
            if (linha) linha.remove();

        } else {
            alert(dados.erro || "Erro ao desativar numero de grupo");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar numero de grupo");
    }
}

async function salvarNovoNumeroGrupo() {
    const numero = document.getElementById("txtAddNumeroGrupo").value.trim();
    const descricao = document.getElementById("txtAddDescricaoNumeroGrupo").value.trim();
    const gravado = document.getElementById("addGravadoNumeroGrupo").checked;
    const iddepartamento = departamentoSelecionadoId;
    const id_tronco = troncoSelecionadoId;

    if (!numero) return alert("Preencha o número do grupo!");
    if (!id_tronco) return alert("Selecione um tronco");

    try {
        const resposta = await fetch("/numerogrupo/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ iddepartamento, numero, descricao, gravado, id_tronco })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            return alert("Erro ao adicionar número de grupo: " + (resultado.erro || resultado.mensagem));
        }

        alert("Número de Grupo adicionado com sucesso!");
        window.location.href = "/numerogrupo";

    } catch (erro) {
        console.error(erro);
        alert("Erro ao adicionar número de grupo.");
    }
}

// ✅ Só isso aqui no final — sem o exemplo errado
document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("searchNumeroGrupo");
    if (!search) return;

    search.addEventListener("input", function () {
        const filtro = this.value.toLowerCase();
        document.querySelectorAll("#tabelaNumeroGrupo tbody tr")
            .forEach(linha => {
                linha.style.display = linha.innerText.toLowerCase().includes(filtro) ? "" : "none";
            });
    });
});

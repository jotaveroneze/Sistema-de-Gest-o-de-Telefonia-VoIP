// ======================= MODAL RAMAL =======================


// 🔹 CHAMAR AO ABRIR O MODAL
function abrirAdicionarRamal() {

    carregarRamalModal();
    carregarTronco();

    // limpa campo
    const inputNome = document.getElementById("txtAddNomeRamal");
    if (inputNome) inputNome.value = "";

    abrirModal("modalAdicionarRamal");
}

// 🔹 CARREGAR RAMAIS (SÓ NO MODAL)
async function carregarRamalModal() {
    try {
        const response = await fetch("/ramal/listar");
        if (!response.ok) throw new Error("Erro ao buscar ramal");

        ramal = await response.json();
        preencherTabelaRamalModal(ramal);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar ramal");
    }
}

async function salvarNovoRamal() {
    const ramalValor = document.getElementById("txtAddRamal").value.trim();
    const gravado1 = document.getElementById("addGravado").checked;
    const id_tronco = troncoSelecionadoId;

    if (!ramalValor) {
        alert("Informe o ramal");
        return;
    }

    if (!id_tronco) {
        alert("Selecione um tronco");
        return;
    }

    const dados = {
        numero: ramalValor,
        idtronco: id_tronco,
        gravado: gravado1 ? 1 : 0
    };

    try {
        const response = await fetch("/ramal/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.erro || "Erro ao adicionar ramal");
            return;
        }

        alert("Ramal adicionado com sucesso!");
        window.location.href = "/ramais"; // ✅ Redireciona após sucesso
    } catch (err) {
        console.error(err);
        alert("Erro ao adicionar ramal");
    }
}



// 🔹 PREENCHER TABELA DO MODAL (COM CHECKBOX)
function preencherTabelaRamalModal(lista) {
    const tbody = document.querySelector("#tabelaRamal tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    lista.forEach(t => {
        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                    <input type="checkbox"
                           class="ramal-checkbox"
                           value="${t.id}">
                </td>
                <td>${t.nome}</td>
            </tr>
        `;
    });
}

async function removerRamal(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este ramal?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/ramal/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`ramal-${id}`);
            if (linha) linha.remove();

            carregarRamal(); // Atualiza tabela
        } else {
            alert(dados.erro || "Erro ao desativar ramal");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar ramal");
    }
}

// 🔹 OBTER RAMAIS SELECIONADOS
function obterRamaisSelecionados() {
    return Array.from(
        document.querySelectorAll(".ramal-checkbox:checked")
    ).map(cb => Number(cb.value));
}


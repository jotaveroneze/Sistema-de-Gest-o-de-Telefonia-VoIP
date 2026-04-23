// ======================= MODAL TRONCO =======================

async function carregarTroncoEditar() {
    try {
        const response = await fetch('/tronco/listar');
        if (!response.ok) throw new Error("Erro ao buscar troncos");

        troncos = await response.json();
        preencherTabelaTroncosEditar(troncos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar troncos");
    }
}


function preencherTabelaTroncosEditar(lista) {
 // IDs das tabelas que podem existir
    const tabelas = ["tabelaTroncoEditar", "tabelaTroncoEditar-NumeroGrupo"];

    tabelas.forEach(idTabela => {
        const tbody = document.querySelector(`#${idTabela} tbody`);
        if (!tbody) return; // pula se a tabela não existir

        tbody.innerHTML = ""; // limpa o corpo da tabela

        lista.forEach(t => {
            tbody.innerHTML += `
                <tr>
                    <td class="text-center">
                        <input type="radio"
                               name="tronco_add"
                               value="${t.id}"
                               onclick="selecionarTroncoModal(${t.id})">
                    </td>
                    <td>${t.numerochave}</td>
                    <td>${t.ramalinicial}</td>
                    <td>${t.ramalfinal}</td>
                    <td>${t.operadora}</td>
                </tr>
            `;
        });
    });
}



async function carregarTronco() {
    try {
        const response = await fetch('/tronco/listar');
        if (!response.ok) throw new Error("Erro ao buscar troncos");

        troncos = await response.json();
        preencherTabelaTroncoModal(troncos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar troncos");
    }
}


// 🔹 CHAMAR AO ABRIR O MODAL
function abrirAdicionarTronco() {

    carregarTroncoModal();


    // limpa campo
    const inputNome = document.getElementById("txtAddNomeTronco");
    if (inputNome) inputNome.value = "";

    troncoSelecionadoId = null;

    abrirModal("modalAdicionarTronco");
}

// 🔹 CARREGAR TRONCOS (SÓ NO MODAL)
async function carregarTroncoModal() {

    try {
        const response = await fetch("/tronco/listar");
        if (!response.ok) throw new Error("Erro ao buscar troncos");

        troncos = await response.json();
        preencherTabelaTroncoModal(troncos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar troncos");
    }
}


async function removerTronco(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este tronco?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/tronco/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`tronco-${id}`);
            if (linha) linha.remove();

            carregarTronco(); // Atualiza tabela
        } else {
            alert(dados.erro || "Erro ao desativar tronco");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar tronco");
    }
}

async function removerTroncoEditar(id) {
    const confirmacao = confirm("Tem certeza que deseja remover este tronco?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/tronco/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`tronco-${id}`);
            if (linha) linha.remove();


        } else {
            alert(dados.erro || "Erro ao desativar tronco");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar tronco");
    }
}

// 🔹 PREENCHER TABELA DO MODAL
function preencherTabelaTroncoModal(lista) {

    const tabelas = ["tabelaTronco", "tabelaTronco-NumeroGrupo"];

    tabelas.forEach(idTabela => {
        const tbody = document.querySelector(`#${idTabela} tbody`);
        if (!tbody) return;

        tbody.innerHTML = "";

        lista.forEach(t => {
            tbody.innerHTML += `
                <tr>
                    <td class="text-center">
                        <input type="radio"
                               name="tronco_add"
                               value="${t.id}"
                               onclick="selecionarTroncoModal(${t.id})">
                    </td>
                    <td>${t.numerochave}</td>
                    <td>${t.ramalinicial}</td>
                    <td>${t.ramalfinal}</td>
                    <td>${t.operadora}</td>
                </tr>
            `;
        });
    });
}

// 🔹 SELECIONAR TRONCO
function selecionarTroncoModal(id) {
    troncoSelecionadoId = id;
    console.log("Tronco selecionado:", id);
}

// 🔹 SALVAR NOVO TRONCO
async function salvarNovoTronco() {
    const numerochave = document.getElementById("txtAddNumerochave").value.trim();
    const ramalInicial = document.getElementById("txtAddRamalincial").value.trim();
    const ramalFinal   = document.getElementById("txtAddRamalfinal").value.trim();

    if (!numerochave) {
        alert("Informe o Número Chave!");
        return;
    }

    if (!ramalInicial || !ramalFinal) {
        alert("Informe o ramal inicial e final!");
        return;
    }

    if (!operadoraSelecionadaId) {
        alert("Selecione uma operadora!");
        return;
    }

    const dados = {
        numerochave,
        ramal_inicial: ramalInicial,
        ramal_final: ramalFinal,
        idoperadora: operadoraSelecionadaId
    };

    try {
        const response = await fetch("/tronco/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.erro || data.mensagem || "Erro ao adicionar tronco");
            return;
        }

        alert("Tronco adicionado com sucesso!");
        window.location.href = "/tronco"; // ✅ Atribuição correta

    } catch (err) {
        console.error(err);
        alert("Erro ao adicionar tronco");
    }
}


function abrirEditarTronco(id) {
    const dep = troncos.find(t => t.id === id);
    if (!dep) return alert("Tronco não encontrado!");

    // 🔥 ID CORRETO
    document.getElementById("editIdTronco").value = dep.id;

    document.getElementById("txtEditNumerochave").value = dep.numerochave;
    document.getElementById("txtEditRamalinicial").value = dep.ramalinicial;
    document.getElementById("txtEditRamalfinal").value = dep.ramalfinal;

    operadoraSelecionadaEditarId = dep.idoperadora;

    carregarOperadorasEditar();

    abrirModal("modalEditarTronco");
}

async function salvarEdicaoTronco() {
    const id = document.getElementById("editIdTronco").value;

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

        const data = await resp.json();
        if (!resp.ok) return alert(data.erro || data.mensagem);

        alert("Tronco atualizado com sucesso!");

        fecharModais();
        carregarTronco();

    } catch (e) {
        console.error(e);
        alert("Erro ao editar tronco");
    }
}



//#region operadora


// =========================
// CARREGAR OPERADORAS
// =========================
async function carregarOperadoras() {
    try {
        const response = await fetch('/operadora/listar');
        if (!response.ok) throw new Error("Erro ao buscar operadoras");

        operadoras = await response.json();
        renderTabelaOperadoras(operadoras);
        renderTabelaOperadorasEditar(operadoras);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar operadoras");
    }
}

// =========================
// RENDER TABELA (ADICIONAR)
// =========================
function renderTabelaOperadoras(lista) {
    const tbody = document.querySelector("#tabelaOperadora tbody");
    tbody.innerHTML = "";

    lista.forEach(op => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="operadoraSelecionada" value="${op.id}"
                    ${op.id === operadoraSelecionadaId ? "checked" : ""}>
            </td>

            <td>${op.nome}</td>
            <td>${op.contrato}</td>
            <td>${op.processo}</td>

        `;

        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('input[name="operadoraSelecionada"]').forEach(radio => {
        radio.addEventListener("change", function () {
            operadoraSelecionadaId = parseInt(this.value);
        });
    });
}

// =========================
// SALVAR NOVA OPERADORA
// =========================
async function salvarNovaOperadora() {
    const nome = document.getElementById("txtAddNome").value.trim();
    const contrato = document.getElementById("txtAddContrato").value.trim();
    const processo = document.getElementById("txtAddProcesso").value.trim();

    if (!nome || !contrato || !processo)
        return alert("Preencha todos os campos!");

    try {
        const resp = await fetch("/operadora/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, contrato, processo })
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert(erro.mensagem || erro.error);
        }

        alert("Operadora adicionada com sucesso!");
        window.location.href = "/operadora"

        fecharModais();
        document.getElementById("formAdicionarOperadora").reset();
        carregarOperadoras();

    } catch (e) {
        console.error(e);
        alert("Erro ao adicionar operadora");
    }
}

// =========================
// REMOVER OPERADORA
// =========================
async function removerOperadora(id) {
    if (!confirm("Deseja remover esta operadora?")) return;

    try {
        const resp = await fetch(`/operadora/remover/${id}`, {
            method: "DELETE"
        });

        const dados = await resp.json();
        if (!resp.ok)
            return alert(dados.erro || dados.mensagem);

        alert(dados.mensagem || "Operadora removida");
        carregarOperadoras();

    } catch (e) {
        console.error(e);
        alert("Erro ao remover operadora");
    }
}

// =========================
// ABRIR MODAL EDITAR
// =========================
function abrirEditarOperadora(id, nome, contrato, processo) {

    document.getElementById("editIdOperadora").value = id;
    document.getElementById("editNomeOperadora").value = nome;
    document.getElementById("editContratoOperadora").value = contrato;
    document.getElementById("editProcessoOperadora").value = processo;

    new bootstrap.Modal(
        document.getElementById("modalEditarOperadora")
    ).show();
}



// =========================
// SALVAR EDIÇÃO
// =========================
async function salvarEdicaoOperadora() {
    const id = document.getElementById("editIdOperadora").value;
    const nome = document.getElementById("editNomeOperadora").value.trim();
    const contrato = document.getElementById("editContratoOperadora").value.trim();
    const processo = document.getElementById("editProcessoOperadora").value.trim();

    if (!nome || !contrato || !processo)
        return alert("Preencha todos os campos!");

    try {
        const resp = await fetch(`/operadora/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, contrato, processo })
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert(erro.mensagem || erro.error);
        }

        alert("Operadora atualizada com sucesso!");

        window.location.href = '/operadora';
        carregarOperadoras();

    } catch (e) {
        console.error(e);
        alert("Erro ao editar operadora");
    }
}

// =========================
// FILTRO (ADICIONAR)
// =========================
document.getElementById("searchOperadora")?.addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    const filtradas = operadoras.filter(o =>
        o.nome.toLowerCase().includes(filtro) ||
        o.contrato.toLowerCase().includes(filtro) ||
        o.processo.toLowerCase().includes(filtro)
    );
    renderTabelaOperadoras(filtradas);
});

// =========================
// FILTRO (EDITAR)
// =========================
document.getElementById("searchOperadoraEdit")?.addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    const filtradas = operadoras.filter(o =>
        o.nome.toLowerCase().includes(filtro) ||
        o.contrato.toLowerCase().includes(filtro) ||
        o.processo.toLowerCase().includes(filtro)
    );
    renderTabelaOperadorasEditar(filtradas);
});

// =========================
// RENDER TABELA (EDITAR)
// =========================
function renderTabelaOperadorasEditar(lista) {
    const tbody = document.querySelector("#tabelaOperadoraEdit tbody");
    tbody.innerHTML = "";

    lista.forEach(op => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="operadoraEdit" value="${op.id}"
                    ${op.id === operadoraSelecionadaEditarId ? "checked" : ""}>
            </td>

            <td>${op.nome}</td>
            <td>${op.contrato}</td>
            <td>${op.processo}</td>
        `;

        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('input[name="operadoraEdit"]').forEach(radio => {
        radio.addEventListener("change", function () {
            operadoraSelecionadaEditarId = parseInt(this.value);
            console.log('Operadora selecionada: ' + operadoraSelecionadaEditarId)
        });
    });
}

function carregarOperadorasEditar() {
    const pesquisa = ""

    const filtradas = operadoras.filter(sec =>
        sec.nome.toLowerCase().includes(pesquisa)
    );

    renderTabelaOperadorasEditar(filtradas);
}

//#endregion


function abrirAdicionarOperadora() {

    // Fecha modal de editar, se estiver aberto
    const modalEditar = bootstrap.Modal.getInstance(
        document.getElementById("modalEditarOperadora")
    );
    if (modalEditar) {
            fecharModais();
    }

    // Limpa formulário de adicionar
    document.getElementById("formAdicionarOperadora").reset();

    // Abre modal de adicionar
    abrirModal("modalAdicionarOperadora");
}


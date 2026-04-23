async function carregarLugarTelefone() {
    try {
        const response = await fetch("/lugartelefone/listar");
        if (!response.ok) throw new Error("Erro ao buscar lugares");

        const data = await response.json();

        // ✅ CORREÇÃO: usa data.data ao invés de data.lugares
        const lugares = data.data || [];
        renderTabelaLugarTelefone(lugares);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar lugares de telefone");
    }
}




function renderTabelaLugarTelefone(lista) {
    const tbody = document.querySelector("#tabelaLugarTelefone tbody");
    tbody.innerHTML = "";

    lista.forEach(l => {
        const tr = document.createElement("tr");

        // verifica se o checkbox deve estar marcado
        const checked = l.id === lugarTelefoneSelecionadoId ? "checked" : "";

        tr.innerHTML = `
            <td>
                <input type="checkbox" ${checked} onclick="selecionarLugarTelefone(${l.id}, this)">
                <strong>${l.nomelugar}</strong><br>
                <small class="text-muted">
                    ${l.departamento ?? ""} • ${l.endereco} • ${l.andar ?? ""}
                </small>
            </td>
            </td>
        `;

        tbody.appendChild(tr);
    });
}


function selecionarLugarTelefone(idLugar, checkbox) {
    if (checkbox.checked) {
        lugarTelefoneSelecionadoId = idLugar;

        // desmarca todos os outros checkboxes
        document
            .querySelectorAll("#tabelaLugarTelefone tbody input[type=checkbox]")
            .forEach(cb => {
                if (cb !== checkbox) cb.checked = false;
            });
    } else {
        lugarTelefoneSelecionadoId = null;
    }
}


document.getElementById("searchLugarTelefone")
?.addEventListener("input", function () {
    const texto = this.value.toLowerCase();

    document
        .querySelectorAll("#tabelaLugarTelefone tbody tr")
        .forEach(tr => {
            tr.style.display =
                tr.innerText.toLowerCase().includes(texto) ? "" : "none";
        });
});



// Abrir modal de edição
async function editarLugarTelefone(id) {
    lugarTelefoneEditarId = id;

    try {
        // Busca os dados do lugar telefone pelo ID
        const response = await fetch(`/lugartelefone/${id}`);
        if (!response.ok) throw new Error("Erro ao buscar lugar telefone");

        const lugar = await response.json();

        // Preenche os campos do modal
        document.getElementById("txtEditarNomeLugarTelefone").value = lugar.nomelugar;
        document.getElementById("txtEditarEnderecoLugarTelefone").value = lugar.endereco;
        document.getElementById("txtEditarAndarLugarTelefone").value = lugar.andar || "";

        // Seleciona departamento no modal de edição
        if (typeof carregarDepartamentosEditar === "function") {
            await carregarDepartamentosEditar(lugar.iddepartamento);
        }

        // Abre o modal

        abrirModal("modalEditarLugarTelefone");

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar dados do lugar telefone");
    }
}

// Salvar alterações
async function salvarEditarLugarTelefone() {
    const nomelugar = document.getElementById("txtEditarNomeLugarTelefone").value.trim();
    const endereco = document.getElementById("txtEditarEnderecoLugarTelefone").value.trim();
    const andar = document.getElementById("txtEditarAndarLugarTelefone").value.trim();

    if (!nomelugar || !endereco) {
        return alert("Preencha todos os campos obrigatórios");
    }

    if (!departamentoSelecionadoEditarId) {
        return alert("Selecione um departamento");
    }

    const payload = {
        nomelugar,
        endereco,
        andar,
        iddepartamento: departamentoSelecionadoEditarId
    };

    try {
        const response = await fetch(`/lugartelefone/editar/${lugarTelefoneEditarId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const erro = await response.json();
            return alert("Erro: " + (erro.mensagem || erro.error));
        }

        // ✅ Fecha o modal antes de redirecionar
        const modal = bootstrap.Modal.getInstance(
            document.getElementById("modalEditarLugarTelefone")
        );
        if (modal) modal.hide();

        alert("Lugar Telefone atualizado com sucesso!");
        window.location.href = '/lugartelefone'; // ✅ = e não ()

    } catch (err) {
        console.error(err);
        alert("Erro ao atualizar lugar telefone");
    }
}



async function removerLugarTelefone(id) {
    if (!confirm("Deseja realmente remover este lugar?")) return;

    try {
        const response = await fetch(`/lugartelefone/remover/${id}`, {
            method: "DELETE"
        });
        if (!response.ok) throw new Error("Erro ao remover lugar");

        alert("Lugar removido com sucesso!");
        carregarLugarTelefone();
    } catch (err) {
        console.error(err);
        alert("Erro ao remover lugar");
    }
}

function abrirAdicionarTelefone() {
    lugarTelefoneSelecionadoId = null;

    carregarLugarTelefone(); // 👈 AQUI ESTAVA FALTANDO

    abrirModal("modalAdicionarTelefone");
}


function abrirAdicionarLugarTelefone() {

    // limpa campos do formulário
    document.getElementById("formAdicionarLugarTelefone").reset();

    // limpa pesquisa de departamento
    const search = document.getElementById("searchDepartamentoLugarTelefone");
    if (search) search.value = "";

    // reseta departamento selecionado (se existir)
    if (typeof departamentoSelecionadoId !== "undefined") {
        departamentoSelecionadoId = null;
    }

    // carrega departamentos na tabela
    if (typeof carregarDepartamentosLugarTelefone === "function") {
        carregarDepartamentosLugarTelefone();
    }

    // abre o modal
    abrirModal("modalAdicionarLugarTelefone");
}

async function salvarLugarTelefone() {
    const nomelugar = document.getElementById("txtAddNomeLugarTelefone").value.trim();
    const endereco = document.getElementById("txtAddEnderecoLugarTelefone").value.trim();
    const andar = document.getElementById("txtAddAndarLugarTelefone").value.trim();

    if (!nomelugar || !endereco) {
        alert("Preencha todos os campos obrigatórios");
        return;
    }

    if (!departamentoSelecionadoId) {
        alert("Selecione um departamento");
        return;
    }

    const payload = {
        nomelugar: nomelugar,
        endereco: endereco,
        andar: andar,
        iddepartamento: parseInt(departamentoSelecionadoId, 10)
    };

    try {
        const response = await fetch("/lugartelefone/criar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Erro ao salvar lugar telefone");
        }

        alert("Lugar Telefone cadastrado com sucesso!");
        window.location.href = "/lugartelefone";
        return;


        // se existir tabela/listagem, recarrega
        if (typeof carregarLugarTelefone === "function") {
            carregarLugarTelefone();
            document.getElementById("txtAddNomeLugarTelefone").value = "";
            document.getElementById("txtAddEnderecoLugarTelefone").value = "";
            document.getElementById("txtAddAndarLugarTelefone").value = "";
        }

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar Lugar Telefone");
    }
}

function selecionarDepartamento(id) {
    departamentoSelecionadoId = id;
    carregarDepartamentos(); // atualiza visual
}

function renderTabelaLugarTelefoneEditar(lista) {
    const tbody = document.querySelector("#tabelaLugarTelefoneEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(l => {
        const checked = l.id === lugarTelefoneSelecionadoEditarId ? "checked" : "";

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <input type="checkbox" ${checked} onclick="selecionarLugarTelefoneEditar(${l.id}, this)">
                <strong>${l.nomelugar}</strong><br>
                <small class="text-muted">
                    ${l.departamento ?? ""} • ${l.endereco} • ${l.andar ?? ""}
                </small>
            </td>

        `;
        tbody.appendChild(tr);
    });
}

function selecionarLugarTelefoneEditar(id, checkbox) {
    if (checkbox.checked) {
        lugarTelefoneSelecionadoEditarId = id;

        document.querySelectorAll("#tabelaLugarTelefoneEditar tbody input[type=checkbox]")
            .forEach(cb => {
                if (cb !== checkbox) cb.checked = false;
            });
    } else {
        lugarTelefoneSelecionadoEditarId = null;
    }
}

async function carregarLugarTelefoneEditar(selecionadoId = null) {
    try {
        const response = await fetch("/lugartelefone/listar");
        if (!response.ok) throw new Error("Erro ao buscar lugares");

        const lugares = await response.json();
        lugarTelefoneSelecionadoEditarId = selecionadoId; // define lugar selecionado
        renderTabelaLugarTelefoneEditar(lugares);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar lugares de telefone para edição");
    }
}

// Filtro dentro do modal de edição
document.getElementById("searchLugarTelefoneEditar")?.addEventListener("input", function () {
    const texto = this.value.toLowerCase();
    document.querySelectorAll("#tabelaLugarTelefoneEditar tbody tr").forEach(tr => {
        tr.style.display = tr.innerText.toLowerCase().includes(texto) ? "" : "none";
    });
});

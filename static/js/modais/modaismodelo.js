//#region windows



// Carregar windowss do banco
async function carregarModelo() {
    try {
        const response = await fetch('/modelo/listar');
        if (!response.ok) throw new Error("Erro ao buscar modelos");
        modelos = await response.json(); // preenche o array global
        preencherTabelaModelo(modelos)
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar modelos");
    }
}

// Remover departamento do backend
async function removerModelo(idModelo) {
    const confirmacao = confirm("Tem certeza que deseja remover este modelo?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/modelo/remover/${idModelo}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`modelo-${idModelo}`);
            if (linha) linha.remove();

            carregarModelo(); // Atualiza tabela
        } else {
            alert(dados.erro || "Erro ao desativar modelo");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar modelo");
    }
}

function selecionarModelo(id, checkbox) {
    if (checkbox.checked) {
        modeloSelecionadoId = id;

        // desmarca todos os outros checkboxes
        document.querySelectorAll(".checkbox-modelo").forEach(cb => {
            if (cb !== checkbox) cb.checked = false;
        });
    } else {
        modeloSelecionadoId = null;
    }
}

function preencherTabelaModelo(lista) {
    const tbody = document.querySelector("#tabelaModelo tbody");
    tbody.innerHTML = "";

    lista.forEach(sis => {
        const checked = sis.id === modeloSelecionadoId ? "checked" : "";

        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                    <input type="checkbox" class="checkbox-modelo" data-id="${sis.id}" ${checked}
                        onclick="selecionarModelo(${sis.id}, this)">
                </td>
                <td>${sis.nome}</td>
            </tr>
        `;
    });
}


function abrirAdicionarModelo() {
    // Se houver modal, abre ele
    abrirModal("modalAdicionarModelo");
}



// Filtrar departamentos ao digitar
document.getElementById("searchModelo").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = modelos.filter(d => d.nome.toLowerCase().includes(filtro));
    preencherTabelaModelo(filtrados); // renderiza apenas os filtrados
});


async function salvarNovoModelo() {
    const modeloNome = document.getElementById("txtAddModelo").value.trim();

    if (!modeloNome) {
        alert("Preencha o Modelo!");
        return;
    }

    try {
        const resposta = await fetch("/modelo/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: modeloNome })
        });

        const resultado = await resposta.json();

        if (resposta[1] == 409){
        alert("Essa empresa já está cadastrada no sistema!");
        return;
        }

        if (!resposta.ok) {
            // ✅ Mostra mensagem de erro do backend (inclusive "já existe")
            alert("Erro: " + (resultado.erro || resultado.mensagem));
            return; // ← para aqui, não redireciona
        }

        alert("Modelo adicionado com sucesso!");
        window.location.href = '/modelo';

    } catch (erro) {
        console.error("Erro ao adicionar modelo:", erro);
        alert("Erro ao adicionar modelo.");
    }
}


// Função para abrir modal de edição
async function abrirEditarModelo(id, nome) {
    document.getElementById("editIdModelo").value = id;
    document.getElementById("editNomeModelo").value = nome;

    try {
        // Carrega todos os departamentos do backend (caso queira mostrar lista ou selecionar)
        const response = await fetch('/modelo/listar');
        if (!response.ok) throw new Error("Erro ao buscar Modelo");
        const modelo = await response.json();

        // Abre o modal
    abrirModal("modalEditarModelo");
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar modelo para edição");
    }
}

// Função para salvar edição
async function salvarEdicaoModelo() {
    const id = document.getElementById("editIdModelo").value;
    const nome = document.getElementById("editNomeModelo").value.trim();

    if (!nome) {
        alert("O nome do modelo é obrigatório!");
        return;
    }

    try {
        const resposta = await fetch(`/modelo/editar/${id}`, {
            method: "PUT", // ou PATCH, dependendo do backend
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert("Erro ao atualizar modelo: " + (resultado.erro || resultado.mensagem));
            return;
        }

        alert("Modelo atualizado com sucesso!");
        window.location.href = '/modelo';

        // Recarrega tabela de departamentos
        carregarModelo();

    } catch (erro) {
        console.error("Erro ao editar modelo:", erro);
        alert("Erro ao editar modelo");
    }
}

function preencherTabelaModeloEditar(lista) {
    const tbody = document.querySelector("#tabelaModeloEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(sis => {
        const checked = sis.id === modeloSelecionadoEditarId ? "checked" : "";

        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                    <input type="checkbox" class="checkbox-modelo-editar" data-id="${sis.id}" ${checked}
                        onclick="selecionarModeloEditar(${sis.id}, this)">
                </td>
                <td>${sis.nome}</td>

            </tr>
        `;
    });
}

function selecionarModeloEditar(id, checkbox) {
    if (checkbox.checked) {
        modeloSelecionadoEditarId = id;

        // desmarca todos os outros checkboxes
        document.querySelectorAll(".checkbox-modelo-editar").forEach(cb => {
            if (cb !== checkbox) cb.checked = false;
        });
    } else {
        modeloSelecionadoEditarId = null;
    }
}

async function carregarModeloEditar(selecionadoId = null) {
    try {
        const response = await fetch('/modelo/listar');
        if (!response.ok) throw new Error("Erro ao buscar modelos");

        const modelos = await response.json();
        modeloSelecionadoEditarId = selecionadoId; // define modelo selecionado
        preencherTabelaModeloEditar(modelos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar modelos para edição");
    }
}

// Filtro dentro do modal de edição
document.getElementById("searchModeloEditar")?.addEventListener("input", function() {
    const filtro = this.value.toLowerCase();
    const filtrados = modelos.filter(m => m.nome.toLowerCase().includes(filtro));
    preencherTabelaModeloEditar(filtrados);
});


//#endregion

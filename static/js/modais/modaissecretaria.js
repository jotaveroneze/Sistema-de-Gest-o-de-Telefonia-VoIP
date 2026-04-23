

// Carregar secretarias do banco
async function carregarSecretarias() {
    try {
        const response = await fetch('/secretaria/listar');
        if (!response.ok) throw new Error("Erro ao buscar secretarias");
        secretarias = await response.json(); // preenche o array global
        renderTabelaSecretarias(secretarias);
        renderTabelaSecretariasEditar(secretarias)
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar secretarias");
    }
}

function renderTabelaSecretarias(lista) {
    const tbody = document.querySelector("#tabelaSecretaria tbody");
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="secretariaSelecionado" value="${dep.id}"
                    ${dep.id === secretariaSelecionadoId ? "checked" : ""}>
            </td>

            <td>${dep.sigla}</td>
            <td>${dep.nome}</td>
        `;

        tbody.appendChild(tr);
    });


    // Atualiza o id do departamento selecionado ao clicar
    tbody.querySelectorAll('input[name="secretariaSelecionado"]').forEach(radio => {
        radio.addEventListener('change', function() {
            secretariaSelecionadoId = parseInt(this.value);
            console.log("Secretaria selecionado:", secretariaSelecionadoId);
        });
    });
}

async function salvarSecretaria() {
    const sigla = document.getElementById("addSigla").value.trim();
    const nome = document.getElementById("addNome").value.trim();

    if (!sigla || !nome) {
        return alert("Preencha todos os campos!");
    }

    const dados = { sigla, nome };

    try {
        const resposta = await fetch("/secretaria/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();  // ✅ 1: Lê o resultado

        // ✅ 2: Verifica 409 PRIMEIRO
        if (resposta.status === 409) {
            alert("Essa secretaria já está cadastrada!");
            return;
        }

        if (!resposta.ok) {
            alert("Erro: " + (resultado.mensagem || resultado.erro || "Erro desconhecido"));
            return;
        }

        // ✅ 3: Só executa se foi sucesso (201)
        document.getElementById("formAdicionarSecretaria")?.reset();
        alert("Secretaria criada com sucesso!");
        window.location.href = "/secretaria";

    } catch (e) {
        console.error(e);
        alert("Erro ao criar secretaria!");
    }
}


// Remover departamento do backend
async function removerSecretaria(id) {
    const confirmacao = confirm("Tem certeza que deseja remover esta secretaria?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/secretaria/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);
        if (typeof carregarSecretarias === "function") {
            carregarSecretarias();
        }
        if (typeof carregarSecretariasEditar === "function") {
            carregarSecretariasEditar();
        }


            // Remove a linha da tabela
            const linha = document.getElementById(`secretaria-${id}`);
            if (linha) linha.remove();

        } else {
            alert(dados.erro || "Erro ao desativar secretaria");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
    }
}

function abrirEditarSecretaria(id) {
    const sec = secretarias.find(x => x.id === id);
    if (!sec) return alert("Secretaria não encontrada!");

    document.getElementById("editarIdSecretaria").value = sec.id;
    document.getElementById("editarSigla").value = sec.sigla;
    document.getElementById("editarNome").value = sec.nome;

    new bootstrap.Modal(document.getElementById("modalEditarSecretaria")).show();
}

async function salvarEdicaoSecretaria() {

    const id = document.getElementById("editarIdSecretaria").value;
    const sigla = document.getElementById("editarSigla").value.trim();
    const nome = document.getElementById("editarNome").value.trim();

    if (!sigla || !nome)
        return alert("Preencha todos os campos!");

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

        alert("Secretaria atualizada com sucesso!");

        fecharModais();
        carregarSecretarias();
        carregarSecretariasEditar()
    } catch (e) {
        console.error(e);
        alert("Erro ao editar secretaria!");
    }
}

function abrirAdicionarSecretaria() {
    abrirModal("modalAdicionarSecretaria");
}


function carregarSecretariasEditar() {
    const pesquisa = document.getElementById("searchSecretariaEditar").value.toLowerCase();

    const filtradas = secretarias.filter(sec =>
        sec.sigla.toLowerCase().includes(pesquisa) ||
        sec.nome.toLowerCase().includes(pesquisa)
    );

    renderTabelaSecretariasEditar(filtradas);
}

function renderTabelaSecretariasEditar(lista) {
    const tbody = document.querySelector("#tabelaSecretariaEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="secretariaEdit" value="${dep.id}"
                    ${dep.id === secretariaSelecionadoEditarId ? "checked" : ""}>
            </td>

            <td>${dep.sigla}</td>
            <td>${dep.nome}</td>
        `;

        tbody.appendChild(tr);
    });

    // Atualizar qual secretaria está selecionada no modal EDITAR
    tbody.querySelectorAll('input[name="secretariaEdit"]').forEach(radio => {
        radio.addEventListener('change', function () {
            secretariaSelecionadoEditarId = parseInt(this.value);
            console.log("Secretaria selecionada para EDITAR:", secretariaSelecionadoEditarId);
        });
    });
}

// FILTRAR SECRETARIAS NO MODAL EDITAR
document.getElementById("searchSecretariaEditar").addEventListener("input", function () {
    let filtro = this.value.toLowerCase();
    let linhas = document.querySelectorAll("#tabelaSecretariaEditar tbody tr");

    linhas.forEach(linha => {
        let texto = linha.innerText.toLowerCase();
        linha.style.display = texto.includes(filtro) ? "" : "none";
    });
});

// FILTRAR SECRETARIAS NO MODAL EDITAR
document.getElementById("searchSecretaria").addEventListener("input", function () {
    let filtro = this.value.toLowerCase();
    let linhas = document.querySelectorAll("#tabelaSecretaria tbody tr");

    linhas.forEach(linha => {
        let texto = linha.innerText.toLowerCase();
        linha.style.display = texto.includes(filtro) ? "" : "none";
    });
});



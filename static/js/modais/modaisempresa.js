// ================================ EMPRESAS ================================================

async function carregarEmpresas() {
    try {
        const response = await fetch("/empresa/listar");
        if (!response.ok) throw new Error("Erro ao buscar empresas");

        empresas = await response.json();
        preencherTabelaEmpresas(empresas);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar empresas");
    }
}

function preencherTabelaEmpresas(lista) {
    const tbody = document.querySelector("#tabelaEmpresas tbody");
    tbody.innerHTML = "";

    lista.forEach(e => {
        tbody.innerHTML += `
            <tr>
                <td class="text-center">
                    <input type="radio"
                           name="empresa_add"
                           value="${e.id}"
                           onclick="selecionarEmpresa(${e.id})">
                </td>
                <td>${e.nome}</td>
            </tr>
        `;
    });
}


function selecionarEmpresa(id) {
    empresaSelecionadoId = id;
    console.log("Empresa selecionada:", id);
}


function abrirAdicionarEmpresa() {
    // Limpa campos do formulário
    const inputNome = document.getElementById("txtAddNomeEmpresa");
    if (inputNome) {
        inputNome.value = "";
    }

    // Garante que nenhuma empresa fique selecionada
    empresaSelecionadoId = null;

    // Abre o modal de adicionar
    abrirModal("modalAdicionarEmpresa");
}


async function removerEmpresa(id) {
    const confirmacao = confirm("Tem certeza que deseja remover esta empresa?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/empresa/remover/${id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);
            carregarEmpresas()

            // Remove a linha da tabela
            const linha = document.getElementById(`empresa-${id}`);
            if (linha) linha.remove();

        } else {
            alert(dados.erro || "Erro ao desativar empresa");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar empresa");
    }
}

async function salvarNovoEmpresa() {
    const empresaNome = document.getElementById("txtAddNomeEmpresa").value.trim();

    if (!empresaNome) {
        alert("Preencha o nome da Empresa!");
        return;
    }

    try {
        const resposta = await fetch("/empresa/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: empresaNome })
        });

        const resultado = await resposta.json();

        // 🔍 Debug temporário — remova depois de resolver
        console.log("Status:", resposta.status, "Resultado:", resultado[1]);

        if (resultado[1] == 409) {
            alert("Essa empresa já está cadastrada no sistema!");
            return;
        }

        else if (!resposta.ok) {
            alert("Erro ao adicionar Empresa: " + (resultado.erro || resultado.mensagem));
            return;
        }

        else {
                alert("Empresa adicionada com sucesso!");
        }


        // ✅ Só chega aqui se realmente foi 201
        document.getElementById("formAdicionar").reset();
        await carregarEmpresas(); // ← aguarda recarregar antes de redirecionar

        window.location.href = "/empresa";

    } catch (erro) {
        console.error("Erro ao adicionar empresa:", erro);
        alert("Erro ao adicionar empresa.");
    }
}



document.getElementById("searchEmpresa").addEventListener("input", function () {
    let filtro = this.value.toLowerCase();
    let linhas = document.querySelectorAll("#tabelaEmpresas tbody tr");

    linhas.forEach(linha => {
        let texto = linha.innerText.toLowerCase();
        linha.style.display = texto.includes(filtro) ? "" : "none";
    });
});

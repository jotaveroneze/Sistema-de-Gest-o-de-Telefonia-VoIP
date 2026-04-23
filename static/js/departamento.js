//#region departamento

// Carregar departamentos do banco
async function carregarDepartamentos() {
    mostrarLoadingTabela();
    try {
        const response = await fetch('/departamento/listar');
        if (!response.ok) throw new Error("Erro ao buscar departamentos");

        departamentos = await response.json();

        preencherTabelaDepartamentos(departamentos);
        atualizarDashboardDepartamentos(departamentos);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar departamentos");
    }
    finally {
        esconderLoadingTabela();
    }
}

function atualizarDashboardDepartamentos(lista) {

    if (!Array.isArray(lista)) return;

    const dadosDashboard = {
        labels: ["Departamentos"],
        valores: [lista.length]
    };

    localStorage.setItem(
        "dashboard_departamento",
        JSON.stringify(dadosDashboard)
    );

}



// Remover departamento do backend
async function removerDepartamento(idDepartamento) {
    const confirmacao = confirm("Tem certeza que deseja remover este departamento?");
    if (!confirmacao) return;

    try {
        const resposta = await fetch(`/departamento/remover/${idDepartamento}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();
        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linha = document.getElementById(`departamento-${idDepartamento}`);
            if (linha) linha.remove();

            carregarDepartamentos(); // Atualiza tabela
        } else {
            alert(dados.erro || "Erro ao desativar departamento");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar departamento");
    }
}


function preencherTabelaDepartamentos(lista) {
    const tabela = document.getElementById("tabelaDepartamento");
    tabela.innerHTML = "";

    lista.forEach(dep => {
        tabela.innerHTML += `
            <tr>
                 <td>${dep.sigla}</td>
                <td>${dep.nome}</td>
                <td>
                <button class="btn btn-warning btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Editar departamento"
                    onclick="abrirEditarDepartamento(${dep.id})">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir departamento"
                    onclick="removerDepartamento(${dep.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
                </td>
            </tr>
        `;
    });
}


// Filtrar departamentos ao digitar
document.getElementById("searchDepartamento").addEventListener("input", function () {
    const filtro = this.value.toLowerCase();

const filtrados = departamentos.filter(d =>
    d.nome.toLowerCase().includes(filtro) ||
    (d.sigla && d.sigla.toLowerCase().includes(filtro))
);


    preencherTabelaDepartamentos(filtrados);
});


async function salvarNovo() {

    const departamentoNome = document.getElementById("txtAddDepartamento").value.trim();
    // Formata o nome do departamento com a secretaria em uppercase

    // Validação

        const idsecretaria = secretariaSelecionadoId;

    if (!idsecretaria) {
        alert("Preencha a Secretaria!");
        return;
    }

    try {
        // Requisição para criar o departamento
        const resposta = await fetch("/departamento/adicionar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: departamentoNome, idsecretaria: idsecretaria })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert("Erro ao adicionar departamento: " + (resultado.erro || resultado.mensagem));
            return;
        }

        alert("Departamento adicionado com sucesso!");

        fecharModais();
        // Limpa formulário
        document.getElementById("formAdicionar").reset();

        // Recarrega tabela de departamentos
        carregarDepartamentos();

    } catch (erro) {
        console.error("Erro ao adicionar departamento:", erro);
        alert("Erro ao adicionar departamento.");
    }
}

// Função para salvar edição
async function salvarEdicaoDepartamento() {

    const id = document.getElementById("editIdDepartamento").value;
    const nome = document.getElementById("editNomeDepartamento").value;
    const idsecretaria = secretariaSelecionadoEditarId;

    if (!nome || !idsecretaria)
        return alert("Preencha todos os campos!");

    const dados = { nome, idsecretaria: parseInt(idsecretaria, 10) };

    try {
        const resp = await fetch(`/departamento/editar/${id}`, {
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
            document.getElementById("modalEditarDepartamento")
        );
        if (modal) modal.hide();

        alert("Departamento atualizado com sucesso!");
        window.location.href = '/departamento';

    } catch (e) {
        console.error(e);
        alert("Erro ao editar departamento!");
    }
}


function abrirEditarDepartamento(id) {
    const dep = departamentos.find(x => x.id === id);
    if (!dep) return alert("Departamento não encontrado!");

    document.getElementById("editIdDepartamento").value = dep.id;
    document.getElementById("editNomeDepartamento").value = dep.nome;

    // 👉 DEFINIR A SECRETARIA SELECIONADA ANTES DE CARREGAR A TABELA
    secretariaSelecionadoEditarId = dep.idsecretaria;

    carregarSecretariasEditar();

    new bootstrap.Modal(document.getElementById("modalEditarDepartamento")).show();
}

document.addEventListener("DOMContentLoaded", () => {
    carregarDepartamentos()
    carregarSecretarias();
});

//#endregion

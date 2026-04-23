// 👉 Função principal: busca usuários e preenche a tabela
async function carregarUsuarios() {
    mostrarLoadingTabela();
    const resposta = await fetch("/usuarios/listar");
    const usuarios = await resposta.json();


    listaUsuarios = usuarios;
    esconderLoadingTabela();
    preencherTabela(usuarios);

}

// 👉 Preenche a tabela com os dados recebidos
function preencherTabela(usuarios) {
    const tabela = document.getElementById("tabela-usuarios");

    tabela.innerHTML = "";

    usuarios.forEach(u => {
        tabela.innerHTML += `
          <tr>
            <td>${u.departamento ?? "-"}</td>
            <td>${u.nome}</td>
            <td>
                <button class="btn btn-link p-0 ms-1" 
                        onclick="copiarEmail('${u.email}')" 
                        title="Copiar e-mail">
                    <i class="fa-solid fa-copy fa-sm"></i>
                </button>
                ${u.email}
            </td>
            <td>${u.ramal}</td>
            <td>${u.adm ? "Sim" : "Não"}</td>

            <td class="text-center">
                <button class="btn btn-secondary btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Resetar Senha"
                    onclick="resetarSenha(${u.id})">
                    <i class="fa-solid fa-key"></i>
                </button>

                <button class="btn btn-warning btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Editar usuário"
                    onclick="abrirEditar(${u.id}, '${u.nome}', '${u.email}', '${u.ramal}', ${u.adm}, '${u.departamento}')">
                    <i class="fa-solid fa-pen"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                    data-bs-toggle="tooltip"
                    data-bs-placement="top"
                    title="Excluir usuário"
                    onclick="removerUsuario(${u.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
          </tr>
        `;
    });
}

// Função para copiar e-mail
function copiarEmail(email) {
    navigator.clipboard.writeText(email)
        .catch(err => console.error("Erro ao copiar:", err));
}


// 👉 Carrega ao abrir a página
carregarUsuarios();



// --------------------------------------------------
// 🔍 FILTROS
// --------------------------------------------------

// Busca texto (nome, email ou departamento)
document.querySelector("input[type='search']").addEventListener("input", function() {
    aplicarFiltros();
});

// Ao clicar no botão FILTRAR
document.querySelector(".btn-outline-secondary").addEventListener("click", function() {
    new bootstrap.Modal(document.getElementById('modalFiltros')).show();
});


// Função principal de filtro
function aplicarFiltros(alerta = false) {

    const busca = document.querySelector("input[type='search']").value.trim().toLowerCase();

    let filtrados = listaUsuarios.filter(u =>
        u.nome.toLowerCase().includes(busca) ||
        u.email.toLowerCase().includes(busca) ||
		u.ramal.toLowerCase().includes(busca)
        //u.departamento.toLowerCase().includes(busca)
    );

    if (alerta && filtrados.length === 0) {
        alert("Nenhum usuário encontrado com esses filtros.");
    }

    preencherTabela(filtrados);
}


// --------------------------------------------------
// 🟦 Funções dos modais
// --------------------------------------------------

// Abrir modal Editar
async function abrirEditar(id, nome, email, ramal, adm, iddepartamento) {
    document.getElementById("editIdUsuario").value = id;
    document.getElementById("editNome").value = nome;
    document.getElementById("editEmail").value = email;
    document.getElementById("editRamal").value = ramal || "";
    document.getElementById("editAdm").checked = adm;

    // 🔹 Atualiza variável global do departamento selecionado no modal de edição
    departamentoSelecionadoEditarId = iddepartamento;

    try {
        // Carrega todos os departamentos do backend
        const response = await fetch('/departamento/listar');
        if (!response.ok) throw new Error("Erro ao buscar departamentos");
        departamentos = await response.json();

        // Renderiza tabela de departamentos no modal de edição
        renderTabelaDepartamentosEditar(departamentos, departamentoSelecionadoEditarId);

        // Abre o modal
        new bootstrap.Modal(document.getElementById('modalEditar')).show();

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar departamentos para edição");
    }
}


async function salvarEdicao() {
    const id = document.getElementById("editIdUsuario").value;
    const nome = document.getElementById("editNome").value.trim();
    const email = document.getElementById("editEmail").value.trim();
    const ramal = document.getElementById("editRamal").value.trim();
    const adm = document.getElementById("editAdm").checked;

    // 🔹 Pega o departamento selecionado (radio button)
    const radioSelecionado = document.querySelector('input[name="departamentoRadioEditar"]:checked');
    const departamento = radioSelecionado ? radioSelecionado.value : null;

    if (!nome || !email) {
        alert("Nome e Email são obrigatórios!");
        return;
    }

    const dados = { nome, email, ramal, adm, departamento };

    try {
        const resposta = await fetch(`/usuarios/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert("Erro: " + (resultado.mensagem || resultado.erro));
            return;
        }

        alert("Usuário atualizado com sucesso!");
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditar"));
        modal.hide();
        fecharModais();
        carregarUsuarios(); // atualiza tabela de usuários
    } catch (e) {
        console.error(e);
        alert("Erro ao atualizar usuário.");
    }
}


// Abrir modal Adicionar
function abrirAdicionar() {
    new bootstrap.Modal(document.getElementById('modalAdicionar')).show();
}

async function salvarNovo() {
    const nome = document.getElementById("addNome").value.trim();
    const email = document.getElementById("addEmail").value.trim();
    const ramal = document.getElementById("addRamal").value.trim();
    const adm = document.getElementById("addAdm").checked;

    // Pega o departamento selecionado
    const iddepartamento = departamentoSelecionadoId;

    // Valida campos obrigatórios
    if (!nome || !email) {
        alert("Nome e Email são obrigatórios!");
        return;
    }


    const dados = {
        nome,
        email,
        ramal,
        adm,
        iddepartamento // ⚠ nome correto esperado pelo backend
    };

    try {
        const resposta = await fetch("/usuarios/criar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert("Erro: " + (resultado.mensagem || resultado.error));
            return;
        }

        alert("Usuário criado com sucesso!");
        window.location.href = "/usuario"

        document.getElementById("formAdicionar").reset();

        // Limpa seleção do departamento
        departamentoSelecionadoId = null;

        // Recarrega tabela de usuários
        carregarUsuarios();

    } catch (e) {
        console.error(e);
        alert("Erro ao criar usuário.");
    }
}


function aplicarFiltrosModal() {

    const nomeFiltro = document.getElementById("filtroNome").value.toLowerCase();
    const emailFiltro = document.getElementById("filtroEmail").value.toLowerCase();
    const ramalFiltro = document.getElementById("filtroRamal").value.toLowerCase();
    const admFiltro = document.getElementById("filtroAdm").value;

    let filtrados = listaUsuarios.filter(u => {

        let passa = true;

        if (nomeFiltro && !u.nome.toLowerCase().includes(nomeFiltro)) passa = false;
        if (emailFiltro && !u.email.toLowerCase().includes(emailFiltro)) passa = false;
        if (ramalFiltro && !u.ramal.toLowerCase().includes(ramalFiltro)) passa = false;

        if (admFiltro === "sim" && !u.adm) passa = false;
        if (admFiltro === "nao" && u.adm) passa = false;

        return passa;
    });

    preencherTabela(filtrados);

    // Fechar modal após aplicar
    fecharModais();
}

async function removerUsuario(idUsuario) {
    // Pergunta de confirmação antes de remover
    const confirmacao = confirm("Tem certeza que deseja remover este usuário?");
    if (!confirmacao) return; // Sai da função se o usuário cancelar

    try {
        const resposta = await fetch(`/usuarios/remover_usuario/${idUsuario}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();

        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linhaUsuario = document.getElementById(`usuario-${idUsuario}`);
            if (linhaUsuario) linhaUsuario.remove();

            carregarUsuarios();
        } else {
            alert(dados.erro || "Erro ao desativar usuário");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar usuário");
    }
}


async function resetarSenha(idUsuario) {
    try {
        const resposta = await fetch(`/usuarios/resetar_senha/${idUsuario}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        const dados = await resposta.json();

        if (resposta.ok) {
            alert(dados.mensagem);

            // Remove a linha da tabela
            const linhaUsuario = document.getElementById(`usuario-${idUsuario}`);
            if (linhaUsuario) linhaUsuario.remove();
            carregarUsuarios()
        } else {
            alert(dados.erro || "Erro ao resetar senha");
        }

    } catch (erro) {
        console.error("Erro na requisição:", erro);
        alert("Erro de rede ao desativar usuário");
    }
}

//#region departamento


// Carregar departamentos do banco
async function carregarDepartamentos() {
    try {
        const response = await fetch('/departamento/listar');
        if (!response.ok) throw new Error("Erro ao buscar departamentos");
        departamentos = await response.json(); // preenche o array global
        renderTabelaDepartamentos(departamentos);
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar departamentos");
    }
}



function renderTabelaDepartamentos(lista) {
    const tbody = document.querySelector("#tabelaDepartamentos tbody");
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>
                <input type="radio" name="departamentoSelecionado" value="${dep.id}" 
                    ${dep.id === departamentoSelecionadoId ? "checked" : ""}>
            </td>
            <td>${dep.nome}</td>
        `;
        tbody.appendChild(tr);
    });

    // Atualiza o id do departamento selecionado ao clicar
    tbody.querySelectorAll('input[name="departamentoSelecionado"]').forEach(radio => {
        radio.addEventListener('change', function() {
            departamentoSelecionadoId = parseInt(this.value);
            console.log("Departamento selecionado:", departamentoSelecionadoId);
        });
    });
}

function renderTabelaDepartamentosEditar(lista, selecionadoId) {
    const tbody = document.querySelector("#tabelaDepartamentosEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="text-center">
                <input type="radio" name="departamentoRadioEditar" value="${dep.id}" ${dep.id === selecionadoId ? "checked" : ""}>
            </td>
            <td>${dep.nome}</td>
        `;

        tbody.appendChild(tr);
    });
}


// Filtrar departamentos ao digitar
document.getElementById("searchDepartamento").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = departamentos.filter(d => d.nome.toLowerCase().includes(filtro));
    renderTabelaDepartamentos(filtrados); // renderiza apenas os filtrados
});

document.getElementById("searchDepartamentoEditar").addEventListener("input", function() {
    const filtro = this.value.toLowerCase(); // texto digitado
    const filtrados = departamentos.filter(d => d.nome.toLowerCase().includes(filtro));
    renderTabelaDepartamentosEditar(filtrados); // renderiza apenas os filtrados
});


//#endregion
document.addEventListener("DOMContentLoaded", () => {
    carregarDepartamentos()
});





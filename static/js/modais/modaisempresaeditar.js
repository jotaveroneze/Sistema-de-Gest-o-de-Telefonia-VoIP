// ================== EMPRESA - EDITAR ==================


// Abre o modal de editar empresa
function abrirEditarEmpresa(id) {
    const emp = empresas.find(e => e.id === id);
    if (!emp) return alert("Empresa não encontrada!");

    // Preenche campos
    document.getElementById("editIdEmpresa").value = emp.id;
    document.getElementById("editNomeEmpresa").value = emp.nome;

    empresaSelecionadoEditarId = emp.id;

    carregarEmpresasEditar();

    // Abre o modal
    abrirModal("modalEditarEmpresa");
}


// Salvar edição
async function salvarEdicaoEmpresa() {
    const id = document.getElementById("editIdEmpresa").value;
    const nome = document.getElementById("editNomeEmpresa").value.trim();

    if (!nome) {
        alert("Preencha todos os campos!");
        return;
    }

    try {
        const resp = await fetch(`/empresa/editar/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome })
        });

        if (!resp.ok) {
            const erro = await resp.json();
            return alert("Erro: " + (erro.error || erro.mensagem));
        }

        alert("Empresa atualizada com sucesso!");

        fecharModais();
        carregarEmpresas();

    } catch (e) {
        console.error(e);
        alert("Erro ao editar empresa!");
    }
}


// Render tabela de empresas no modal editar
function renderTabelaEmpresasEditar(lista) {
    const tbody = document.querySelector("#tabelaEmpresasEditar tbody");
    tbody.innerHTML = "";

    lista.forEach(emp => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="empresaEdit" value="${emp.id}"
                    ${emp.id === empresaSelecionadoEditarId ? "checked" : ""}>
            </td>

            <td>${emp.nome}</td>

        `;

        tbody.appendChild(tr);
    });

    // Atualiza seleção
    tbody.querySelectorAll('input[name="empresaEdit"]').forEach(radio => {
        radio.addEventListener("change", function () {
            empresaSelecionadoEditarId = parseInt(this.value);
            console.log("Empresa selecionada para EDITAR:", empresaSelecionadoEditarId);
        });
    });
}


// Filtro de pesquisa
document.getElementById("searchEmpresaEditar").addEventListener("input", function () {
    const filtro = this.value.toLowerCase();
    const linhas = document.querySelectorAll("#tabelaEmpresasEditar tbody tr");

    linhas.forEach(linha => {
        linha.style.display = linha.innerText.toLowerCase().includes(filtro)
            ? ""
            : "none";
    });
});


function carregarEmpresasEditar() {

    if (!empresas || empresas.length === 0) {
        console.warn("Empresas ainda não carregadas, tentando novamente...");
        carregarEmpresas().then(() => carregarEmpresasEditar());
        return;
    }

    const pesquisa = document.getElementById("searchEmpresaEditar").value.toLowerCase();

    const filtradas = empresas.filter(emp =>
        emp.nome.toLowerCase().includes(pesquisa)
    );

    renderTabelaEmpresasEditar(filtradas);
}


// Abre o modal de editar departamento
function abrirEditarDepartamento(id) {
    const dep = departamentos.find(x => x.id === id);
    if (!dep) return alert("Departamento não encontrado!");

    // Preenche os campos do modal
    document.getElementById("editIdDepartamento").value = dep.id;
    document.getElementById("editNomeDepartamento").value = dep.nome;


    carregarDepartamentosEditar();

    // Abre o modal correto

    abrirModal("modalEditarDepartamento");
}

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

        alert("Departamento atualizado com sucesso!");
        window.location.href = '/departamento'; // ✅ Redireciona após o alert

    } catch (e) {
        console.error(e);
        alert("Erro ao editar departamento!");
    }
}



function renderTabelaDepartamentosEditar(lista) {
    const tbody = document.querySelector("#tabelaDepartamentosEditar tbody");
    if(!tbody) return;
    tbody.innerHTML = "";

    lista.forEach(dep => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>
                <input type="radio" name="departamentoEdit" value="${dep.id}"
                    ${dep.id === departamentoSelecionadoEditarId ? "checked" : ""}>
            </td>

            <td>${dep.sigla ?? "_"}</td>
            <td>${dep.nome} ?? "_"</td>

        `;

        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('input[name="departamentoEdit"]').forEach(radio => {
        radio.addEventListener("change", function () {
            departamentoSelecionadoEditarId = parseInt(this.value);
            console.log("Departamento selecionado para EDITAR:", departamentoSelecionadoEditarId);
        });
    });
}


// ✅ só registra o evento quando o modal é aberto
document.getElementById("modalEditarDepartamento")
    .addEventListener("shown.bs.modal", function () {
        const input = document.getElementById("searchDepartamentoEditar");
        if (!input) return;

        input.addEventListener("input", function () {
            const filtro = this.value.toLowerCase();
            document.querySelectorAll("#tabelaDepartamentosEditar tbody tr")
                .forEach(linha => {
                    linha.style.display =
                        linha.innerText.toLowerCase().includes(filtro) ? "" : "none";
                });
        });
    });


function carregarDepartamentosEditar() {

    const pesquisa = document.getElementById("searchDepartamentoEditar").value.toLowerCase();

    const filtradas = departamentos.filter(sec =>
        sec.sigla.toLowerCase().includes(pesquisa) ||
        sec.nome.toLowerCase().includes(pesquisa)
    );
    renderTabelaDepartamentosEditar(filtradas);
}


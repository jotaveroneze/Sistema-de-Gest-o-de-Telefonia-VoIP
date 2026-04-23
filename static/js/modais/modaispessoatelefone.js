async function visualizarPessoasTelefone(idTelefone, textoTelefone) {

    telefonePessoaAtual = idTelefone;

    document.getElementById("labelTelefonePessoa").innerText = textoTelefone;
    document.getElementById("labelAdicionarTelefonePessoa").innerText = textoTelefone;

    const tbody = document.getElementById("tbodyPessoasTelefone");
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-muted">Carregando...</td>
            </tr>
        `;
    }

    const modalElement = document.getElementById("modalVisualizarPessoasTelefone");

    if (!modalVisualizarPessoasTelefoneInstance) {
        modalVisualizarPessoasTelefoneInstance = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
    }

    modalVisualizarPessoasTelefoneInstance.show();

    try {
        const response = await fetch(`/pessoatelefone/listar/${idTelefone}`);
        const dados = await response.json();

        preencherTabelaPessoasTelefone(dados);

    } catch (e) {
        console.error(e);
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-danger">
                        Erro ao carregar pessoas
                    </td>
                </tr>
            `;
        }
    }
}


function preencherTabelaPessoasTelefone(lista) {
    const tbody = document.querySelector("#tabelaPessoasTelefone tbody");
    tbody.innerHTML = "";

    if (!lista.length) {
        tbody.innerHTML = `
          <tr>
            <td colspan="5" class="text-center text-muted">
              Nenhuma pessoa vinculada
            </td>
          </tr>`;
        return;
    }

    lista.forEach(p => {
        tbody.innerHTML += `
          <tr>
            <td>${p.nome}</td>
            <td>${p.funcional || "-"}</td>
            <td>${p.cpf || "-"}</td>
            <td>${p.departamento || "-"}</td>
            <td class="text-center">
              <button class="btn btn-outline-danger btn-sm"
                onclick="removerPessoaTelefone(${p.id_vinculo})">
                <i class="fa-solid fa-unlink"></i>
              </button>
            </td>
          </tr>
        `;
    });
}

async function removerPessoaTelefone(idVinculo) {
    if (!confirm("Deseja remover esta pessoa do telefone?")) return;

    await fetch(`/pessoatelefone/${idVinculo}`, { method: "DELETE" });

    visualizarPessoasTelefone(telefonePessoaAtual,
        document.getElementById("labelTelefonePessoa").innerText);
}

async function abrirModalAdicionarPessoaTelefone() {
    pessoasSelecionadas.clear();

    const response = await fetch(`/pessoatelefone/disponiveis/${telefonePessoaAtual}`);
    pessoasDisponiveis = await response.json();

    const tbody = document.querySelector("#tabelaAdicionarPessoaTelefone tbody");
    tbody.innerHTML = "";

    pessoasDisponiveis.forEach(p => {
        tbody.innerHTML += `
          <tr>
            <td>
              <input type="checkbox"
                onchange="togglePessoa(${p.id}, this)">
            </td>
            <td>${p.nome}</td>
            <td>${p.funcional || "-"}</td>
            <td>${p.cpf || "-"}</td>
          </tr>`;
    });

       abrirModal("modalAdicionarPessoaTelefone");
}

function togglePessoa(id, cb) {
    cb.checked ? pessoasSelecionadas.add(id)
               : pessoasSelecionadas.delete(id);
}

async function salvarPessoaTelefone() {
    await fetch("/pessoatelefone/vincular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            idtelefone: telefonePessoaAtual,
            pessoas: Array.from(pessoasSelecionadas)
        })
    });

        fecharModaisVinculo();
    visualizarPessoasTelefone(telefonePessoaAtual,
        document.getElementById("labelTelefonePessoa").innerText);
}


document
  .getElementById("searchPessoaAdicionarTelefone")
  ?.addEventListener("input", function () {

    const texto = this.value.toLowerCase();

    const filtrados = pessoasDisponiveis.filter(p =>
      String(p.nome || "").toLowerCase().includes(texto) ||
      String(p.funcional || "").toLowerCase().includes(texto) ||
      String(p.cpf || "").includes(texto)
    );

    renderTabelaAdicionarPessoa(filtrados);
});


function renderTabelaAdicionarPessoa(lista) {
    const tbody = document.querySelector("#tabelaAdicionarPessoaTelefone tbody");
    tbody.innerHTML = "";

    if (!lista.length) {
        tbody.innerHTML = `
          <tr>
            <td colspan="4" class="text-center text-muted">
              Nenhuma pessoa encontrada
            </td>
          </tr>`;
        return;
    }

    lista.forEach(p => {
        tbody.innerHTML += `
          <tr>
            <td>
              <input type="checkbox"
                     ${pessoasSelecionadas.has(p.id) ? "checked" : ""}
                     onchange="togglePessoa(${p.id}, this)">
            </td>
            <td>${p.nome}</td>
            <td>${p.funcional || "-"}</td>
            <td>${p.cpf || "-"}</td>
          </tr>
        `;
    });
}



/* 🔄 CARREGAR GARANTIAS */
async function carregarGarantias() {
    try {
        const response = await fetch("/garantia/listar");
        if (!response.ok) throw new Error("Erro ao buscar garantias");

        const garantias = await response.json();
        preencherTabelaGarantias(garantias);

    } catch (err) {
        console.error(err);
        alert("Erro ao carregar garantias");
    }
}

function preencherTabelaGarantias(lista) {
    const tbody = document.getElementById("tabelaTelefonesGarantia");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!lista || lista.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    Nenhum telefone em garantia
                </td>
            </tr>
        `;
        return;
    }

    lista.forEach(g => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${g.telefone?.patrimonio || "-"}</td>
            <td>${g.telefone?.serial || "-"}</td>

            <td>
                ${g.dataentrada
                    ? new Date(g.dataentrada).toLocaleDateString("pt-BR")
                    : "-"}
            </td>

            <td>
                ${g.datasaida
                    ? new Date(g.datasaida).toLocaleDateString("pt-BR")
                    : "<span class='badge bg-warning text-dark'>Em aberto</span>"}
            </td>

            <td>${g.defeito || "-"}</td>

            <td>${g.solucao || "-"}</td>

            <td class="text-center">
                <button class="btn btn-success btn-sm me-1"
                        title="Devolver da garantia"
                        onclick="abrirModalSolucao(${g.id})">
                    <i class="fa-solid fa-rotate-left"></i>
                </button>

                <button class="btn btn-danger btn-sm"
                        title="Excluir garantia"
                        onclick="excluirGarantia(${g.id})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const abaGarantia = document.querySelector(
        '[data-bs-target="#tab-garantia"]'
    );

    if (!abaGarantia) {
        console.warn("Aba de garantia não encontrada");
        return;
    }

    abaGarantia.addEventListener("shown.bs.tab", () => {
        carregarGarantias();
    });
});

async function excluirGarantia(id) {
    if (!confirm("Deseja remover esta garantia?")) return;

    try {
        const res = await fetch(`/garantia/excluir/${id}`, {
            method: "PUT"
        });

        if (!res.ok) throw new Error();

        carregarGarantias();

    } catch (err) {
        console.error(err);
        alert("Erro ao excluir garantia");
    }
}

let garantiaIdAtual = null;

  // Mantendo seu padrão: abrir modal e salvar o ID
  function abrirModalSolucao(idGarantia) {
    garantiaIdAtual = idGarantia;
    const modal = new bootstrap.Modal(document.getElementById('modalSolucao'));
    modal.show();
  }

  // Função chamada ao clicar no botão do modal
  async function confirmarDevolucao() {
    const solucao = document.getElementById('descricaoSolucao').value.trim();
    if (!solucao) {
      alert("Por favor, descreva a solução antes de enviar.");
      return;
    }

    // Mantendo confirmação padrão
    if (!confirm("Deseja devolver este telefone da garantia?")) return;

    fecharModais();
    // Chama a função original de devolver, agora enviando solução
    await devolverGarantia(garantiaIdAtual, solucao);
  }

  // Função original, adaptada para receber solução
  async function devolverGarantia(id, solucao = "") {
    try {
      const res = await fetch(`/garantia/devolver/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ solucao }) // envia a solução
      });

      if (!res.ok) throw new Error();

      carregarGarantias(); // recarrega tabela

    } catch (err) {
      console.error(err);
      alert("Erro ao devolver garantia");
    }
  }




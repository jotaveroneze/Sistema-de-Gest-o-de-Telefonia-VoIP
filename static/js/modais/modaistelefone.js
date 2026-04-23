async function abrirAdicionarTelefone() {
    // limpa formulário
    document.getElementById("formAdicionarTelefone").reset();

    // abre modal
    abrirModal("modalAdicionarTelefone");
}

async function salvarTelefone() {

    const idmodelo = modeloSelecionadoId;
    const idlugarlocal = lugarTelefoneSelecionadoId;

    if (!idmodelo || !idlugarlocal) {
        alert("Selecione um Modelo e um Lugar de Telefone");
        return;
    }

    const payload = {
        patrimonio: document.getElementById("addpatrimonio").value.trim(),
        serial: document.getElementById("addserial").value.trim(),
        macaddress: document.getElementById("addmacaddress").value.trim(),
        nometelefone: document.getElementById("addnometelefone").value.trim(),
        processocompra: document.getElementById("addprocessocompra").value.trim(),
        notafiscal: document.getElementById("addnotafiscal").value.trim(),
        montado: document.getElementById("addmontado").checked,
        patrimoniado: document.getElementById("addpatrimoniado").checked,
        defeito: document.getElementById("adddefeito").checked,
        idmodelo,
        idlugarlocal
    };

    try {
        const response = await fetch("/telefone/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        // Ao invés de alert + redirect, usa isso:
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Erro ao adicionar telefone");
        }

        const result = await response.json(); // ✅ espera o JSON de confirmação do servidor
        alert("Telefone cadastrado com sucesso!");
        window.location.href = "/telefone";


    } catch (err) {
        console.error(err);
        alert(err.message);
    }
}

async function removerTelefone(id) {
    if (!confirm("Deseja realmente excluir este telefone?")) return;

    try {
        const response = await fetch(`/telefone/remover_telefone/${id}`, {
            method: "DELETE",
        });

        const resultado = await response.json();

        if (!response.ok) {
            throw new Error(resultado.erro || "Erro ao remover telefone");
        }

        alert(resultado.mensagem); // mensagem do backend
        carregarTelefones(); // atualiza tabela após desativar

    } catch (err) {
        console.error(err);
        alert(err.message);
    }
}

// Abrir modal de edição
async function abrirEditarTelefone(id) {
    telefoneEditarId = id;

    try {
        const response = await fetch(`/telefone/editar/${id}`);
        if (!response.ok) throw new Error("Erro ao buscar telefone");

        const t = await response.json();

        // Preenche campos do modal
        document.getElementById("editIdTelefone").value = t.id;
        document.getElementById("editpatrimonio").value = t.patrimonio || "";
        document.getElementById("editserial").value = t.serial || "";
        document.getElementById("editmacaddress").value = t.macaddress || "";
        document.getElementById("editnometelefone").value = t.nometelefone || "";
        document.getElementById("editprocessocompra").value = t.processocompra || "";
        document.getElementById("editnotafiscal").value = t.notafiscal || "";
        document.getElementById("editmontado").checked = t.montado;
        document.getElementById("editpatrimoniado").checked = t.patrimoniado;
        document.getElementById("editdefeito").checked = t.defeito;

        // Selecionar modelo e lugar
        telefoneModeloSelecionadoId = t.idmodelo;
        telefoneLugarSelecionadoId = t.idlugarlocal;

        // Carregar modelos e lugares na tabela do modal
        if (typeof carregarModeloEditar === "function") await carregarModeloEditar(t.idmodelo);
        if (typeof carregarLugarTelefoneEditar === "function") await carregarLugarTelefoneEditar(t.idlugarlocal);

        // Abrir modal
        abrirModal("modalEditarTelefone");
    } catch (err) {
        console.error(err);
        alert("Erro ao carregar telefone para edição");
    }
}

async function salvarEdicaoTelefone() {
  const patrimonio = document.getElementById("editpatrimonio").value.trim();

  if (!/^\d+$/.test(patrimonio)) {
    alert("O campo Patrimônio deve conter apenas números.");
    return;
  }

  if (!modeloSelecionadoEditarId) {
    alert("Selecione um Modelo antes de salvar.");
    return;
  }

  if (!lugarTelefoneSelecionadoEditarId) {
    alert("Selecione um Lugar de Telefone antes de salvar.");
    return;
  }

  const payload = {
    patrimonio,
    serial: document.getElementById("editserial").value.trim(),
    macaddress: document.getElementById("editmacaddress").value.trim(),
    nometelefone: document.getElementById("editnometelefone").value.trim(),
    processocompra: document.getElementById("editprocessocompra").value.trim(),
    notafiscal: document.getElementById("editnotafiscal").value.trim(),
    montado: document.getElementById("editmontado").checked,
    patrimoniado: document.getElementById("editpatrimoniado").checked,
    defeito: document.getElementById("editdefeito").checked,
    idmodelo: modeloSelecionadoEditarId,
    idlugarlocal: lugarTelefoneSelecionadoEditarId
  };

  try {
    const response = await fetch(`/telefone/editar/${telefoneEditarId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      // tenta pegar mensagem do backend (sem quebrar se vier vazio)
      const txt = await response.text();
      throw new Error(txt || "Erro ao atualizar telefone");
    }

    alert("Telefone atualizado com sucesso!");
    window.location.href = "/telefone"; // redireciona
    return;

  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}


